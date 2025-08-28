export interface SearchResult {
  export_name: string
  key: string
  question: string
  context: string
  field_title: string
  score: number
  rank: number
  confidence_percent: number
  highlighted_question?: string
}

export interface SearchResponse {
  results: SearchResult[]
  query: string
  strategy: string
  elapsed_ms: number
  total_results: number
}