import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:28000'
const API_SECRET = process.env.API_SECRET || 'formally_secret_key_2024'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // In production, verify JWT token here
    // const token = request.headers.get('authorization')
    // await verifyJWT(token)
    
    console.log('Connecting to backend:', BACKEND_URL)
    
    // Proxy to backend with API secret
    const response = await fetch(`${BACKEND_URL}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Secret': API_SECRET,
      },
      body: JSON.stringify(body),
    })
    
    if (!response.ok) {
      throw new Error(`Backend search failed: ${response.status}`)
    }
    
    const data = await response.json()
    return NextResponse.json(data)
    
  } catch (error: any) {
    console.error('Search API error:', error)
    console.error('Backend URL:', BACKEND_URL)
    
    // Check if backend is running
    if (error.cause?.code === 'ECONNREFUSED') {
      return NextResponse.json(
        { error: 'Backend service is not running. Please run: cd backend && docker-compose up -d' },
        { status: 503 }
      )
    }
    
    return NextResponse.json(
      { error: 'Search failed', details: error.message },
      { status: 500 }
    )
  }
}