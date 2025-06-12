import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    console.log('NFT check request:', body)

    // Мок-данные для разработки
    // В продакшене здесь будет реальная проверка NFT
    const mockResponse = {
      has_access: true,
      access_level: 'basic',
      nfts: [
        {
          collection: 'NeuroNest Access Collection',
          tokenId: '1',
          name: 'NeuroNest Access Pass #1',
          image: '/icon-192.svg',
          verified: true,
          description: 'Эксклюзивный доступ к NeuroNest AI Marketplace'
        }
      ],
      total_nfts: 1,
      debug_info: {
        wallet_checked: body.wallet_address || 'unknown',
        allowed_collections: ['EQCGbQyAJxxMsYQWLCklkXQq4fkIBK3kz3GA1TkFJyUR9nTH'],
        raw_nfts_count: 1,
        valid_nfts_count: 1
      }
    }

    return NextResponse.json(mockResponse)
  } catch (error) {
    console.error('Error in check-nft:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// Добавляем OPTIONS для CORS
export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  })
}