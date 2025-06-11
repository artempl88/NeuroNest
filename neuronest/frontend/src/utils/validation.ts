import { NFTAccessData } from '../types'

export const validateNFTAccessData = (data: any): NFTAccessData => {
  if (!data || typeof data !== 'object') {
    throw new Error('Invalid NFT access data')
  }
  
  return {
    has_access: Boolean(data.has_access),
    access_level: data.access_level || 'none',
    nfts: Array.isArray(data.nfts) ? data.nfts : [],
    total_nfts: Number(data.total_nfts) || 0,
    fallback_mode: data.fallback_mode,
    debug_info: data.debug_info
  }
} 