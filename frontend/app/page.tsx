'use client'

import { useState, useCallback, useEffect } from 'react'
import { Search, Clock, Database, Zap } from 'lucide-react'
import { SearchResponse, SearchResult } from '@/lib/types'

export default function HomePage() {
  const [query, setQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const [memoryResults, setMemoryResults] = useState<SearchResponse | null>(null)
  const [postgresResults, setPostgresResults] = useState<SearchResponse | null>(null)
  const [loadingMemory, setLoadingMemory] = useState(false)
  const [loadingPostgres, setLoadingPostgres] = useState(false)
  const [isDevView, setIsDevView] = useState(false)

  // Debounce logic
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query)
    }, 300)
    return () => clearTimeout(timer)
  }, [query])

  // Trigger searches on debounced query change
  useEffect(() => {
    if (!debouncedQuery.trim()) {
      setMemoryResults(null)
      setPostgresResults(null)
      return
    }

    // In dev view, search both strategies in parallel
    // In user view, only search with memory (fastest)
    if (isDevView) {
      searchWithStrategy('memory')
      searchWithStrategy('postgres')
    } else {
      searchWithStrategy('memory')
      setPostgresResults(null)
    }
  }, [debouncedQuery, isDevView])

  const searchWithStrategy = async (strategy: string) => {
    const setLoading = strategy === 'memory' ? setLoadingMemory : setLoadingPostgres
    const setResults = strategy === 'memory' ? setMemoryResults : setPostgresResults
    
    setLoading(true)
    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query: debouncedQuery, 
          strategy, 
          top_n: 5
        }),
      })
      
      if (response.ok) {
        const data = await response.json()
        setResults(data)
      }
    } catch (error) {
      console.error(`Search error (${strategy}):`, error)
    } finally {
      setLoading(false)
    }
  }

  const toggleKey = (key: string) => {
    const newExpanded = new Set(expandedKeys)
    if (newExpanded.has(key)) {
      newExpanded.delete(key)
    } else {
      newExpanded.add(key)
    }
    setExpandedKeys(newExpanded)
  }

  const ResultCard = ({ result, index }: { 
    result: SearchResult | null, 
    index: number
  }) => {
    if (!result) return null
    
    // Create unique identifier for each result
    const uniqueId = `${result.key}_${index}`

    return (
      <div 
        className="bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-700 hover:border-blue-500 transition-colors cursor-pointer"
        onClick={() => toggleKey(uniqueId)}
      >
        <div className="flex justify-between items-start mb-2">
          <span className="text-xs text-gray-400">Rank #{result.rank}</span>
          <span className={`text-sm font-medium px-2 py-1 rounded ${
            result.confidence_percent > 80 ? 'bg-green-900 text-green-300' :
            result.confidence_percent > 50 ? 'bg-yellow-900 text-yellow-300' :
            'bg-red-900 text-red-300'
          }`}>
            {result.confidence_percent.toFixed(0)}%
          </span>
        </div>
        
        <h4 className="font-medium text-gray-100 mb-2 text-base">
          {result.highlighted_question ? (
            <span 
              className="[&_mark]:bg-yellow-900 [&_mark]:text-yellow-200 [&_mark]:px-0.5"
              dangerouslySetInnerHTML={{ __html: result.highlighted_question }} 
            />
          ) : (
            result.question
          )}
        </h4>
        
        <div className="space-y-1 text-xs">
          {result.context && (
            <div>
              <span className="text-gray-500">Context: </span>
              <span className="text-gray-400">{result.context}</span>
            </div>
          )}
          
          {result.field_title && (
            <div>
              <span className="text-gray-500">Field Title: </span>
              <span className="text-gray-400">{result.field_title}</span>
            </div>
          )}
          
          <div>
            <span className="text-gray-500">Export Name: </span>
            <span className="text-gray-400">{result.export_name}</span>
          </div>
          
          <div>
            <span className="text-gray-500">Key: </span>
            <span className="font-mono text-blue-300">{result.key}</span>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <h1 className="text-3xl font-bold text-center mb-8 text-white">
          Formally Search System
        </h1>
        
        {/* Search Bar */}
        <div className="max-w-2xl mx-auto mb-8">
          <div className="relative mb-3">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search for a form field..."
              className="w-full pl-10 pr-4 py-3 text-lg bg-gray-800 border border-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-400"
              autoFocus
            />
          </div>
          
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-2 text-sm text-gray-400">
              <input
                type="checkbox"
                checked={isDevView}
                onChange={(e) => setIsDevView(e.target.checked)}
                className="rounded border-gray-600 bg-gray-700 text-blue-500"
              />
              Dev View (A/B Testing)
            </label>
            
            {isDevView && (
              <span className="text-xs text-gray-500">
                PostgreSQL FTS requires 3+ characters
              </span>
            )}
          </div>
        </div>

        {/* Results Section */}
        {isDevView ? (
          // Dev View: Side-by-side A/B Testing
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* In-Memory Results */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold flex items-center gap-2 text-white">
                  <Zap className="w-5 h-5 text-yellow-500" />
                  In-Memory Index
                </h2>
                {memoryResults && (
                  <div className="flex items-center gap-2 text-sm text-gray-400">
                    <Clock className="w-4 h-4" />
                    {memoryResults.elapsed_ms.toFixed(1)}ms
                  </div>
                )}
              </div>
              
              {loadingMemory && (
                <div className="flex justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                </div>
              )}
              
              {!loadingMemory && memoryResults && (
                <div className="space-y-3">
                  {memoryResults.results.length > 0 ? (
                    memoryResults.results.map((result, idx) => (
                      <ResultCard key={`memory_${idx}`} result={result} index={idx} />
                    ))
                  ) : (
                    <div className="text-gray-500 text-center py-4">No results found</div>
                  )}
                </div>
              )}
            </div>

            {/* PostgreSQL Results */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold flex items-center gap-2 text-white">
                  <Database className="w-5 h-5 text-blue-500" />
                  PostgreSQL FTS
                </h2>
                {postgresResults && (
                  <div className="flex items-center gap-2 text-sm text-gray-400">
                    <Clock className="w-4 h-4" />
                    {postgresResults.elapsed_ms.toFixed(1)}ms
                  </div>
                )}
              </div>
              
              {loadingPostgres && (
                <div className="flex justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                </div>
              )}
              
              {!loadingPostgres && postgresResults && (
                <div className="space-y-3">
                  {postgresResults.results.length > 0 ? (
                    postgresResults.results.map((result, idx) => (
                      <ResultCard key={`postgres_${idx}`} result={result} index={idx} />
                    ))
                  ) : (
                    <div className="text-gray-500 text-center py-4">No results found</div>
                  )}
                </div>
              )}
            </div>
          </div>
        ) : (
          // User View: Single search results
          <div className="max-w-3xl mx-auto">
            {memoryResults && (
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-white">
                  Search Results
                </h2>
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <span>{memoryResults.results.length} results</span>
                  <span>•</span>
                  <Clock className="w-4 h-4" />
                  <span>{memoryResults.elapsed_ms.toFixed(1)}ms</span>
                </div>
              </div>
            )}
            
            {loadingMemory && (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              </div>
            )}
            
            {!loadingMemory && memoryResults && (
              <div className="space-y-3">
                {memoryResults.results.length > 0 ? (
                  memoryResults.results.map((result, idx) => (
                    <ResultCard key={`result_${idx}`} result={result} index={idx} />
                  ))
                ) : (
                  debouncedQuery && (
                    <div className="text-gray-500 text-center py-8">
                      No results found for "{debouncedQuery}"
                    </div>
                  )
                )}
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  )
}