import pandas as pd
import numpy as np
from collections import defaultdict
import re
from typing import List, Dict, Tuple
import asyncio
import asyncpg
from sqlalchemy import create_engine, text
import math

from models import SearchResult
from advanced_search import SmartTokenizer, FormFieldNER

class InMemorySearch:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.df = None
        self.inverted_index = defaultdict(set)
        self.doc_norms = {}
        self.idf = {}
        self.documents = []
        self.smart_tokenizer = SmartTokenizer()
        
    def tokenize(self, text: str, is_query: bool = False) -> List[str]:
        """Use smart tokenizer with NER and linguistic processing"""
        return self.smart_tokenizer.tokenize(text, is_query=is_query)
    
    def build_index(self):
        """Build inverted index from CSV data"""
        self.df = pd.read_csv(self.data_path)
        self.df = self.df.fillna("")
        
        # Build document list and index
        for idx, row in self.df.iterrows():
            # Store question tokens separately for questions_only mode
            question_tokens = self.tokenize(row['question'])
            
            # Combine searchable fields for full search
            searchable_text = f"{row['question']} {row['context']} {row.get('fieldTitle', '')}"
            tokens = self.tokenize(searchable_text)
            
            # Build inverted index
            token_freq = defaultdict(int)
            for token in tokens:
                self.inverted_index[token].add(idx)
                token_freq[token] += 1
            
            # Store document
            self.documents.append({
                'id': idx,
                'export_name': row['export_name'],
                'key': row['key'],
                'question': row['question'],
                'context': row['context'],
                'field_title': row.get('fieldTitle', ''),
                'tokens': tokens,
                'question_tokens': question_tokens,
                'token_freq': dict(token_freq)
            })
        
        # Calculate IDF
        num_docs = len(self.documents)
        for token, doc_ids in self.inverted_index.items():
            self.idf[token] = math.log(num_docs / len(doc_ids))
        
        # Calculate document norms
        for doc in self.documents:
            norm = 0
            for token, freq in doc['token_freq'].items():
                tf = 1 + math.log(freq) if freq > 0 else 0
                norm += (tf * self.idf.get(token, 0)) ** 2
            self.doc_norms[doc['id']] = math.sqrt(norm) if norm > 0 else 1
    
    def search(self, query: str, top_n: int = 5, questions_only: bool = False) -> List[SearchResult]:
        """Search using TF-IDF scoring"""
        query_tokens = self.tokenize(query, is_query=True)
        if not query_tokens:
            return []
        
        # Find matching documents
        doc_scores = defaultdict(float)
        query_norm = 0
        
        # Calculate query vector
        query_freq = defaultdict(int)
        for token in query_tokens:
            query_freq[token] += 1
        
        # Score documents
        for token in query_tokens:
            if token not in self.inverted_index:
                continue
                
            query_tf = 1 + math.log(query_freq[token])
            query_weight = query_tf * self.idf.get(token, 0)
            query_norm += query_weight ** 2
            
            for doc_id in self.inverted_index[token]:
                doc = self.documents[doc_id]
                doc_tf = 1 + math.log(doc['token_freq'].get(token, 0)) if token in doc['token_freq'] else 0
                doc_weight = doc_tf * self.idf.get(token, 0)
                
                doc_scores[doc_id] += query_weight * doc_weight
        
        # Normalize scores
        query_norm = math.sqrt(query_norm) if query_norm > 0 else 1
        for doc_id in doc_scores:
            doc_scores[doc_id] /= (query_norm * self.doc_norms[doc_id])
        
        # Boost exact key prefix matches
        query_upper = query.upper()
        for doc in self.documents:
            if doc['key'].startswith(query_upper):
                doc_scores[doc['id']] *= 2.0
        
        # Sort and deduplicate by key
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Remove duplicates by tracking seen keys
        seen_keys = set()
        unique_results = []
        
        for doc_id, score in sorted_docs:
            doc = self.documents[doc_id]
            if doc['key'] not in seen_keys:
                seen_keys.add(doc['key'])
                unique_results.append((doc_id, score))
                if len(unique_results) >= top_n:
                    break
        
        results = []
        for rank, (doc_id, score) in enumerate(unique_results, 1):
            doc = self.documents[doc_id]
            
            # Highlight matches
            highlighted = self.highlight_text(doc['question'], query_tokens)
            
            # Calculate confidence: normalize score to percentage
            # High confidence: exact match or very high TF-IDF score
            # Confidence = min(100, score * 100) for normalized scores
            # For TF-IDF scores typically 0-1, we scale appropriately
            confidence = min(100.0, score * 100)
            
            # Boost confidence for exact matches
            if query.lower() in doc['question'].lower():
                confidence = min(100.0, confidence * 1.5)
            
            results.append(SearchResult(
                export_name=doc['export_name'],
                key=doc['key'],
                question=doc['question'],
                context=doc['context'],
                field_title=doc['field_title'],
                score=score,
                rank=rank,
                confidence_percent=confidence,
                highlighted_question=highlighted
            ))
        
        return results
    
    def highlight_text(self, text: str, query_tokens: List[str]) -> str:
        """Highlight matching tokens in text"""
        highlighted = text
        for token in query_tokens:
            pattern = re.compile(f'\\b{re.escape(token)}\\b', re.IGNORECASE)
            highlighted = pattern.sub(f'<mark>{token}</mark>', highlighted)
        return highlighted


class PostgresFTSSearch:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        
    async def initialize(self):
        """Initialize database and create FTS index"""
        self.engine = create_engine(self.database_url)
        
        # Create table if not exists
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS questions (
                    id SERIAL PRIMARY KEY,
                    export_name TEXT,
                    key TEXT,
                    question TEXT,
                    context TEXT,
                    field_title TEXT,
                    search_vector tsvector
                )
            """))
            conn.commit()
            
            # Check if data exists
            result = conn.execute(text("SELECT COUNT(*) FROM questions"))
            count = result.scalar()
            
            if count == 0:
                # Load data
                df = pd.read_csv("data/state_library.csv")
                df = df.fillna("")
                
                for _, row in df.iterrows():
                    conn.execute(text("""
                        INSERT INTO questions (export_name, key, question, context, field_title, search_vector)
                        VALUES (:export_name, :key, :question, :context, :field_title,
                                to_tsvector('english', :searchable))
                    """), {
                        'export_name': row['export_name'],
                        'key': row['key'],
                        'question': row['question'],
                        'context': row['context'],
                        'field_title': row.get('fieldTitle', ''),
                        'searchable': f"{row['question']} {row['context']} {row.get('fieldTitle', '')}"
                    })
                conn.commit()
                
                # Create GIN index
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_search_vector 
                    ON questions USING GIN(search_vector)
                """))
                conn.commit()
    
    async def search(self, query: str, top_n: int = 5, questions_only: bool = False) -> List[SearchResult]:
        """Search using PostgreSQL FTS"""
        # Require minimum 3 characters for FTS
        if len(query.strip()) < 3:
            return []
            
        with self.engine.connect() as conn:
            # Boost exact key prefix matches
            results = conn.execute(text("""
                SELECT 
                    export_name, key, question, context, field_title,
                    ts_rank(search_vector, query) as rank,
                    CASE 
                        WHEN key LIKE :key_prefix THEN ts_rank(search_vector, query) * 2
                        ELSE ts_rank(search_vector, query)
                    END as boosted_rank
                FROM questions, 
                     plainto_tsquery('english', :query) query
                WHERE search_vector @@ query
                ORDER BY boosted_rank DESC
                LIMIT :limit
            """), {
                'query': query,
                'key_prefix': f"{query.upper()}%",
                'limit': top_n
            })
            
            search_results = []
            for rank, row in enumerate(results, 1):
                # Highlight matches (simplified)
                highlighted = row.question
                for token in query.split():
                    pattern = re.compile(f'\\b{re.escape(token)}\\b', re.IGNORECASE)
                    highlighted = pattern.sub(f'<mark>{token}</mark>', highlighted)
                
                # Calculate confidence based on PostgreSQL rank
                # ts_rank returns values typically between 0 and 1
                confidence = min(100.0, float(row.boosted_rank) * 100)
                if query.lower() in row.question.lower():
                    confidence = min(100.0, confidence * 1.5)
                
                search_results.append(SearchResult(
                    export_name=row.export_name,
                    key=row.key,
                    question=row.question,
                    context=row.context or "",
                    field_title=row.field_title or "",
                    score=float(row.boosted_rank),
                    rank=rank,
                    confidence_percent=confidence,
                    highlighted_question=highlighted
                ))
            
            return search_results