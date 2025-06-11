export const isDemoMode = () => {
  return process.env.NEXT_PUBLIC_DEMO_MODE === 'true'
}

export const getDemoNFTs = () => {
  return [{
    collection: 'demo',
    tokenId: '1',
    name: 'NeuroNest Access Pass #1 (Demo)',
    image: '/icon-192.svg',
    verified: true,
    description: 'Demo NFT for development'
  }]
} 