from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import time
import os
from dotenv import load_dotenv

from search_strategies import InMemorySearch, PostgresFTSSearch
from models import SearchResult, SearchRequest, SearchResponse

load_dotenv()

app = FastAPI(title="Formally Search API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize search strategies
memory_search = InMemorySearch("data/state_library.csv")
postgres_search = PostgresFTSSearch(os.getenv("DATABASE_URL"))

# Initialize both strategies on startup
@app.on_event("startup")
async def startup_event():
    memory_search.build_index()
    await postgres_search.initialize()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "strategies": ["memory", "postgres"]}

@app.post("/search", response_model=SearchResponse)
async def search(
    request: SearchRequest
):
    start_time = time.time()
    
    # Select strategy
    if request.strategy == "memory":
        results = memory_search.search(request.query, request.top_n, request.questions_only)
    elif request.strategy == "postgres":
        results = await postgres_search.search(request.query, request.top_n, request.questions_only)
    else:
        results = memory_search.search(request.query, request.top_n, request.questions_only)  # Default
    
    elapsed_time = (time.time() - start_time) * 1000  # Convert to ms
    
    return SearchResponse(
        results=results,
        query=request.query,
        strategy=request.strategy,
        elapsed_ms=elapsed_time,
        total_results=len(results)
    )

@app.get("/strategies")
async def get_strategies():
    return {
        "strategies": [
            {"id": "memory", "name": "In-Memory Index", "description": "Fast TF-IDF based search"},
            {"id": "postgres", "name": "PostgreSQL FTS", "description": "Production-ready full-text search"}
        ]
    }