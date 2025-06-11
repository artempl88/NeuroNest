import { CONFIG } from '../constants/config'
import type { AccessLevel } from '../types'

export const getAccessLevel = (nftCount: number): AccessLevel => {
  if (nftCount === 0) return 'none'
  if (nftCount >= CONFIG.ACCESS_LEVELS.PREMIUM_MIN) return 'premium'
  if (nftCount >= CONFIG.ACCESS_LEVELS.ADVANCED_MIN) return 'advanced'
  return 'basic'
}

export const formatAddress = (address: string): string => {
  if (!address) return ''
  return `${address.slice(0, 6)}...${address.slice(-6)}`
}

export const getAccessLevelColor = (level: AccessLevel): string => {
  switch (level) {
    case 'premium':
      return 'text-yellow-400'
    case 'advanced':
      return 'text-purple-400'
    case 'basic':
      return 'text-green-400'
    case 'none':
    default:
      return 'text-gray-400'
  }
}

export const getAccessLevelBadge = (level: AccessLevel): string => {
  switch (level) {
    case 'premium':
      return 'bg-yellow-400/20'
    case 'advanced':
      return 'bg-purple-400/20'
    case 'basic':
      return 'bg-green-400/20'
    case 'none':
    default:
      return 'bg-gray-400/20'
  }
} 