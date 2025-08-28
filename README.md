# search-formally

Interview question from formally. Formallly helps people fill out important forms that requires accuracy and help people with the application process that are critical to their lives.

## Important Decisions

- N=5: Optimal for form fields (users rarely check beyond top-5)
- Algorithm: In-memory index (fastest) + Postgres FTS (production-ready) with A/B testing
- Accuracy Priority: 1M records is computationally small but cognitively large. Need robust disambiguation UI with field context, examples, and confidence scores. User verification > algorithmic perfection.

## Search Strategy Implementation

1. **Index**: question + context + fieldTitle
2. **Boost**: Exact key prefix matches (H1B → H1B_* fields)
3. **Group**: Results by key prefix to avoid confusion
4. **Display**: Context prominently for disambiguation

## Form Context Display

- **Key prefix indicates form type**: H1B_*, O1A_*, O1B_* for visa categories
- **Address hierarchy**: US_CURRENT_ADDRESS_* vs CURRENT_ADDRESS_* vs FOREIGN_ADDRESS_*
- **Visual grouping**: Results should show form section (e.g., "H1B Application", "Recommender Info")
- **Duplicate detection**: Same question in different contexts must show all relevant forms
- **Context clarity**: Critical for forms where same field appears in multiple sections

## Critical Data Insights

- **Duplicate questions with different keys**: Same question maps to multiple form contexts - must show all relevant keys
- **Key grouping opportunity**: Related fields share prefixes (US_CURRENT_ADDRESS_*) - group for error detection
- **User-facing text needs improvement**: Next A/B test should compare original vs improved question clarity

## Hierarchical Search (Important Enhancement)

- Form sections as hierarchy: "Immigration Status" → "Visa Types" → "H1B Questions"
- Enables progressive narrowing of search space
- Critical for 1M+ scale navigation

## Confidence Scoring

- **Calculation**: TF-IDF/FTS scores normalized to 0-100%
- **Boosting**: Exact substring matches get 1.5x confidence
- **Interpretation**: >80% = High confidence, 50-80% = Medium, <50% = Low

## Lookahead Considerations

- **300ms debounce**: Balance between responsiveness and server load
- **Not critical for forms**: Unlike general search, form fields need exact matches not discovery
- **Better approach**: Show field groups/categories instead of pure lookahead

## Security & Authentication

- **Current**: API_SECRET proxy through NextJS (development)
- **Production**: JWT authentication with user sessions
- **Assumption**: User auth handled at gateway level
- **No direct backend access**: All requests proxied through NextJS API routes

## Self-Learning & Improvement

1. **Click tracking**: Log which result users select for each query
2. **Relevance feedback**: Track if users abandon search or refine query
3. **Query logs**: Identify common misspellings and synonyms
4. **A/B testing**: Compare strategies to find optimal approach
5. **Reinforcement**: Boost scores for frequently selected results

## Evaluation Strategy

1. **Precision@5**: % of queries with correct answer in top-5
2. **Click-through position**: Average position of clicked result  
3. **Query abandonment**: % of searches with no selection
4. **Duplicate key detection**: Flag when same query returns different keys
5. **Time to selection**: Speed of user finding correct field
6. **Confidence accuracy**: Correlation between confidence % and actual selection

## Run Instructions

### Backend (Docker)
```bash
cd backend
docker-compose up -d  # PostgreSQL on :25432, FastAPI on :28000
```

### Frontend (NextJS)
```bash
cd frontend
pnpm install
pnpm dev  # Runs on http://localhost:23000
```

## Documentation

1. Starting with README here, then read the requirements in `docs/PRD.md` and data in `backend/data/*`
2. `docs/ARCHITECTURE.md` for architecture design and discussions
3. `docs/TASKS.md` for tasks
4. `./CLAUDE.md` or `./AUGMENT.md` for AI notes

