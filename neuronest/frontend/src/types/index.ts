import { LucideIcon } from 'lucide-react'
import { Wallet } from '@tonconnect/ui-react'

export interface NFT {
  collection: string
  tokenId: string
  name: string
  image: string
  verified: boolean
  description?: string
}

export interface AIAgent {
  name: string
  description: string
  price: number
  rating: number
  icon: LucideIcon
  category: string
}

export interface TelegramUser {
  id: number
  first_name: string
  last_name?: string
  username?: string
  language_code?: string
  is_premium?: boolean
  photo_url?: string
}

export interface HapticFeedback {
  impact: (style: 'light' | 'medium' | 'heavy') => void
  notification: (type: 'error' | 'success' | 'warning') => void
  selection: () => void
}

export interface TelegramWebApp {
  initData: string
  initDataUnsafe: {
    user?: TelegramUser
    chat_instance?: string
    chat_type?: string
    start_param?: string
    auth_date?: number
    hash?: string
  }
  version: string
  platform: string
  colorScheme: 'light' | 'dark'
  themeParams: Record<string, string>
  isExpanded: boolean
  viewportHeight: number
  viewportStableHeight: number
  headerColor: string
  backgroundColor: string
  isClosingConfirmationEnabled: boolean
  isVerticalSwipesEnabled: boolean
  
  // Methods
  ready: () => void
  expand: () => void
  close: () => void
  MainButton: {
    text: string
    color: string
    textColor: string
    isVisible: boolean
    isProgressVisible: boolean
    isActive: boolean
    setText: (text: string) => void
    onClick: (callback: () => void) => void
    show: () => void
    hide: () => void
  }
  HapticFeedback: HapticFeedback
  showAlert: (message: string, callback?: () => void) => void
  showConfirm: (message: string, callback?: (confirmed: boolean) => void) => void
  showPopup: (params: {
    title?: string
    message: string
    buttons?: Array<{
      id?: string
      type?: 'default' | 'ok' | 'close' | 'cancel' | 'destructive'
      text: string
    }>
  }, callback?: (buttonId: string) => void) => void
}

export interface WalletSectionProps {
  wallet: Wallet | null
  userFriendlyAddress: string
  hasNFTAccess: boolean
  getAccessLevel: () => AccessLevel
}

export interface AIAgentCardProps {
  agent: AIAgent
  index: number
  onExecute: (name: string, price: number) => void
}

export interface UseNFTAccessProps {
  userFriendlyAddress: string | null
  hapticFeedback: HapticFeedback | null
}

export interface UseNFTAccessReturn {
  hasNFTAccess: boolean
  userNFTs: NFT[]
  isCheckingNFTs: boolean
  checkNFTAccess: () => Promise<void>
}

export interface UseTonTransactionReturn {
  executeAgent: (agentName: string, price: number, userId?: string) => Promise<any>
  isProcessing: boolean
}

export type AccessLevel = 'none' | 'basic' | 'advanced' | 'premium'

export interface NFTAccessData {
  has_access: boolean
  access_level: AccessLevel
  nfts: NFT[]
  total_nfts: number
  fallback_mode?: boolean
  debug_info?: {
    wallet_checked: string
    allowed_collections: string[]
    raw_nfts_count: number
    valid_nfts_count: number
  }
}

export interface ApiError {
  message: string
  code?: string
  status?: number
}

export type TonConnectError = {
  name: 'TonConnectError'
  message: string
  code?: number
} 