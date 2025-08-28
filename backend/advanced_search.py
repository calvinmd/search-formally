"""
Advanced search with NER and linguistic processing
"""
import re
from typing import List, Dict, Set, Tuple
from rapidfuzz import fuzz, process
import pandas as pd

class FormFieldNER:
    """Named Entity Recognition for form fields"""
    
    def __init__(self):
        # Form-specific entity patterns
        self.entity_patterns = {
            'ADDRESS': [
                r'\b(street|address|apt|apartment|suite|floor|unit|city|state|country|province)\b',
                r'\b(current|previous|foreign|mailing|home|work)\s+(address)\b',
            ],
            'POSTAL': [
                r'\b(zip\s*code?|postal\s*code?|zipcode|postalcode)\b',
                r'\b\d{5}(-\d{4})?\b',  # US ZIP
            ],
            'NAME': [
                r'\b(first|last|middle|full|maiden|nick)\s*(name)\b',
                r'\b(name|surname|given\s*name)\b',
            ],
            'DATE': [
                r'\b(date|dob|birth\s*date|expiry|expire|start|end|from|to)\b',
                r'\b(month|year|day)\b',
            ],
            'CONTACT': [
                r'\b(email|e-mail|phone|mobile|cell|fax|telephone)\b',
                r'\b(contact|reach)\b',
            ],
            'ID': [
                r'\b(ssn|social\s*security|passport|license|visa|ein|tin)\b',
                r'\b(number|id|identifier)\b',
            ],
            'IMMIGRATION': [
                r'\b(h1b|o1a|o1b|eb1|eb2|i-94|i-20|ds-2019)\b',
                r'\b(visa|status|petition|immigration)\b',
            ],
        }
        
        # Common form field variations (handles compounds)
        self.field_synonyms = {
            'zipcode': ['zip code', 'zip-code', 'postal code', 'postcode', 'zip'],
            'email': ['e-mail', 'email address', 'electronic mail'],
            'phone': ['telephone', 'phone number', 'tel', 'mobile', 'cell'],
            'address': ['addr', 'location', 'residence'],
            'apartment': ['apt', 'unit', 'suite', 'flat'],
            'firstname': ['first name', 'given name', 'forename'],
            'lastname': ['last name', 'surname', 'family name'],
            'dob': ['date of birth', 'birth date', 'birthday'],
            'ssn': ['social security number', 'social security', 'ss#'],
        }
        
        # Build reverse mapping for quick lookup
        self.synonym_map = {}
        for canonical, variants in self.field_synonyms.items():
            for variant in variants:
                self.synonym_map[variant.lower()] = canonical
            self.synonym_map[canonical] = canonical
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text"""
        text_lower = text.lower()
        entities = {}
        
        for entity_type, patterns in self.entity_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, text_lower, re.IGNORECASE)
                matches.extend(found)
            
            if matches:
                entities[entity_type] = list(set(matches))
        
        return entities
    
    def normalize_query(self, query: str) -> Tuple[str, List[str]]:
        """Normalize query and extract key terms"""
        query_lower = query.lower()
        normalized_terms = []
        
        # Check for known synonyms and normalize
        for phrase in sorted(self.synonym_map.keys(), key=len, reverse=True):
            if phrase in query_lower:
                canonical = self.synonym_map[phrase]
                normalized_terms.append(canonical)
                query_lower = query_lower.replace(phrase, canonical)
        
        # Also keep original terms for fallback
        original_terms = re.findall(r'\b[a-z0-9]+\b', query.lower())
        
        return query_lower, list(set(normalized_terms + original_terms))


class SmartTokenizer:
    """Intelligent tokenization with linguistic awareness"""
    
    def __init__(self):
        self.ner = FormFieldNER()
        
    def tokenize(self, text: str, is_query: bool = False) -> List[str]:
        """Smart tokenization with entity recognition"""
        if pd.isna(text) or not text:
            return []
        
        text = str(text).lower()
        tokens = []
        
        # Standard tokenization
        standard_tokens = re.findall(r'\b[a-z0-9]+\b', text)
        tokens.extend(standard_tokens)
        
        if is_query:
            # For queries, normalize and add synonyms
            normalized, terms = self.ner.normalize_query(text)
            tokens.extend(terms)
        else:
            # For indexing, extract entities and add variants
            entities = self.ner.extract_entities(text)
            
            # Add entity-based tokens
            for entity_type, values in entities.items():
                tokens.extend(values)
            
            # Add known variations for indexing
            for canonical, variants in self.ner.field_synonyms.items():
                if canonical in text or any(v in text for v in variants):
                    tokens.append(canonical)
                    tokens.extend([v.replace(' ', '') for v in variants])
        
        # Deduplicate
        return list(set(tokens))
    
    def fuzzy_match_score(self, query: str, field: str) -> float:
        """Calculate fuzzy match score between query and field"""
        # Use different algorithms for different match types
        scores = [
            fuzz.ratio(query, field) / 100.0,  # Simple ratio
            fuzz.token_sort_ratio(query, field) / 100.0,  # Token sort
            fuzz.token_set_ratio(query, field) / 100.0,  # Token set
        ]
        
        # Boost for exact substring match
        if query.lower() in field.lower():
            scores.append(1.0)
        
        # Return weighted average
        return max(scores) * 0.7 + sum(scores) / len(scores) * 0.3