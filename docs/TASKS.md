# TASKS

## Process

### Rules

Most IMPORTANT RULE: You are acting as the best software architecture in the world. You are here to perform critical thinking and present reasons for your decisions. Do not be agreeable, but be critical and thorough in your considerations, including accuracy, quality, performance, security, and maintainability.

- One task at a time
- Due to the time limit, prioritize function over hygiene (keep basic hygiene)
- Use the safe lts versions for any package
- Limit the new files, dependencies, but keep the code base well componentized and structured
- Do NOT make assumptions, always verify before implement
- One task at a time, and requires manual approval before moving on to the next task

## TODOs

- [ ] 0.0.0 Let's discuss the architecture and design
  - [ ] Describe your understand of the requriements and initial thoughts of possible approaches for both immediate solution and optimal solution
  - [ ] Discuss the following with me: What are some of the best approaches? Top-K? TEXT_SEARCH (Postgres)? Semantic search (although not allowed in this test, but for real implementation, everything is on the table). Any reason to use DAG or GRAPH searches? Any search algo could be useful here?

- [ ] 0.0.1 Build a quick end-to-end working prototype
  - [x] Use a monorepo to keep things simple
  - [x] Data stored in backend/data/
  - [ ] frontend/ use NextJS, pnpm, set up basic prettier and linting, tailwindcss, magic-ui or shadcn components
  - [ ] backend/ use Python Fast API, use python -m ruff for formatting and linting, use docker to spin up a Postgres or REDIS (faster), actual storage TBD
  - [ ] trackers:
    - [ ] backend: support search strategy id to support A/B testing
    - [ ] frontend: add side-by-side comparisons, in a tabular format, for result + time
  - [ ] build a simple search bar with look ahead functionality and matches highlighted
  - [ ] assume N=5, display the top results in ranking order
  - [ ] when clicked, show the retrieved key for the best match

- [ ] 0.0.2 Metrics
  - [ ] Add timer to each execution
  - [ ] How to simulate a 1M+ dataset?
  - [ ] Add A/B testing to compare different approaches
- [ ] Add options and scalability solutions

## Backlog: IGNORE everything below here. These are for human notes
