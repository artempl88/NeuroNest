export const getAccessLevel = (nftCount: number): string => {
  if (nftCount === 0) return 'none'
  if (nftCount >= 10) return 'premium'
  if (nftCount >= 3) return 'advanced'
  return 'basic'
}

export const formatAddress = (address: string) => {
  if (!address) return ''
  return `${address.slice(0, 6)}...${address.slice(-6)}`
} 