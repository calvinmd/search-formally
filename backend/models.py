from pydantic import BaseModel
from typing import List, Optional

class SearchResult(BaseModel):
    export_name: str
    key: str
    question: str
    context: Optional[str] = ""
    field_title: Optional[str] = ""
    score: float
    rank: int
    confidence_percent: float
    highlighted_question: Optional[str] = None

class SearchRequest(BaseModel):
    query: str
    top_n: int = 5
    strategy: str = "memory"  # "memory" or "postgres"
    questions_only: bool = False

class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str
    strategy: str
    elapsed_ms: float
    total_results: int