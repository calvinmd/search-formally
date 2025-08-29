# Formally Search System - Project Context

## Overview
A scalable search system for Formally's form field dataset, implementing keyword-based search with <1s response time for 1M+ records.

## Architecture Decisions
- **Dual Strategy**: In-memory inverted index (fast) + PostgreSQL FTS (production-ready) for A/B testing
- **No Semantic Search**: Rejected due to accuracy requirements - form filling needs 100% precision
- **Deduplication**: Results deduplicated by key to prevent showing same field multiple times
- **Confidence Scoring**: 0-100% based on TF-IDF scores and exact match boosts

## Port Configuration
```bash
# Frontend: http://localhost:23000
# Backend API: http://localhost:28000
# PostgreSQL: localhost:25432
```

## Running the Project

### Backend (Docker)
```bash
cd backend
docker-compose up --build
```

### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```

## Key Features
- **Live Search**: 300ms debounced search-as-you-type
- **Dev View Toggle**: Switch between single search (user) and A/B testing (developer)
- **All Fields Visible**: Shows question, context, field_title, export_name, and key
- **Smart Tokenization**: Handles compound words (zipcode ’ zip code)
- **Highlighting**: Yellow highlights on matched terms
- **Dark Mode UI**: Gray-900 background with subtle borders

## Search Strategies

### In-Memory Index
- TF-IDF scoring with inverted index
- Instant results for any query length
- Smart tokenization with NER
- Key prefix boosting (2x multiplier)

### PostgreSQL FTS
- GIN indexed full-text search
- Requires 3+ character queries
- Production-ready with persistence
- Plainto_tsquery for natural language

## API Endpoints
- `POST /api/search` - Main search endpoint
  - `query`: Search term
  - `strategy`: "memory" or "postgres"
  - `top_n`: Number of results (default: 5)
- `GET /health` - Health check
- `GET /strategies` - List available strategies

## Data Schema
```python
SearchResult:
  - export_name: str (form export identifier)
  - key: str (unique field key)
  - question: str (form field question)
  - context: str (additional context)
  - field_title: str (field title/label)
  - score: float (relevance score)
  - rank: int (result position)
  - confidence_percent: float (0-100)
  - highlighted_question: str (with <mark> tags)
```

## Testing Commands
```bash
# Lint and typecheck (if configured)
npm run lint
npm run typecheck

# Test search API
curl -X POST http://localhost:28000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "zipcode", "strategy": "memory", "top_n": 5}'
```

## UI Components

### ResultCard
- Shows all fields without accordion/expansion
- Confidence badge with color coding:
  - Green (>80%): High confidence
  - Yellow (50-80%): Medium confidence  
  - Red (<50%): Low confidence
- Hover effect on border (blue highlight)

### Search Interface
- Search icon in input field
- Dev View checkbox for A/B testing
- Side-by-side comparison in dev mode
- Single column in user mode
- Response time display with clock icon

## Important Notes
- PostgreSQL FTS requires minimum 3 characters
- Duplicate keys are filtered from results
- Key prefix matches get 2x score boost
- Exact question matches boost confidence by 1.5x
- All text processing preserves original casing in display

## File Structure
```
frontend/
  app/
    page.tsx          # Main search interface
    api/search/       # API proxy endpoint
backend/
  main.py             # FastAPI application
  search_strategies.py # Core search implementations
  advanced_search.py   # NER and tokenization
  models.py           # Pydantic models
  docker-compose.yml  # Container orchestration
```

## User Preferences
- Dark mode interface (gray-900 background)
- Subtle highlighting (yellow-900 bg, yellow-200 text)
- All fields always visible (no hiding/expansion)
- Clean, minimal UI without unnecessary animations
- Practical implementation over theoretical perfection