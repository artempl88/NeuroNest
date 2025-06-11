import { useState, useEffect, useCallback } from 'react'
import toast from 'react-hot-toast'
import { CONFIG } from '../constants/config'
import type { UseNFTAccessProps, UseNFTAccessReturn, NFT, NFTAccessData } from '../types'

export const useNFTAccess = ({ userFriendlyAddress, hapticFeedback }: UseNFTAccessProps): UseNFTAccessReturn => {
  const [hasNFTAccess, setHasNFTAccess] = useState(false)
  const [userNFTs, setUserNFTs] = useState<NFT[]>([])
  const [isCheckingNFTs, setIsCheckingNFTs] = useState(false)
  const [hasCheckedOnce, setHasCheckedOnce] = useState(false)

  const checkNFTAccess = useCallback(async () => {
    if (!userFriendlyAddress || isCheckingNFTs) return

    setIsCheckingNFTs(true)
    try {
      const response = await fetch(`${CONFIG.API_URL}/api/v1/wallet/check-nft`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ wallet_address: userFriendlyAddress })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const nftData: NFTAccessData = await response.json()
      
      setUserNFTs(nftData.nfts || [])
      setHasNFTAccess(nftData.has_access || false)
      setHasCheckedOnce(true)
      
      if (!hasCheckedOnce) {
        if (nftData.has_access) {
          hapticFeedback?.notification('success')
          toast.success(`🎉 NFT доступ подтвержден! Уровень: ${nftData.access_level}`)
        } else {
          toast.error('❌ NFT не найдены в разрешенных коллекциях')
        }
      }
      
    } catch (error) {
      console.error('Ошибка проверки NFT:', error)
      handleNFTError(error)
    } finally {
      setIsCheckingNFTs(false)
    }
  }, [userFriendlyAddress, hapticFeedback, isCheckingNFTs, hasCheckedOnce])

  const handleNFTError = useCallback((error: any) => {
    if (error instanceof TypeError && error.message.includes('NetworkError')) {
      if (!hasCheckedOnce) {
        toast.error('Сервер недоступен. Проверьте подключение.')
      }
    } else {
      if (!hasCheckedOnce) {
        toast.error('Ошибка проверки NFT коллекций')
      }
    }
    
    hapticFeedback?.notification('error')
    
    const mockNFTs: NFT[] = [{
      collection: 'demo',
      tokenId: '1',
      name: 'NeuroNest Access Pass #1 (Demo)',
      image: 'https://via.placeholder.com/300x300/00FFFF/000000?text=NEURONEST',
      verified: true,
      description: 'Demo NFT for development'
    }]
    
    setUserNFTs(mockNFTs)
    setHasNFTAccess(true)
    setHasCheckedOnce(true)
    
    if (!hasCheckedOnce) {
      toast.success('🔄 Демо режим активирован')
    }
  }, [hapticFeedback, hasCheckedOnce])

  useEffect(() => {
    if (userFriendlyAddress && !hasCheckedOnce && !isCheckingNFTs) {
      const timer = setTimeout(() => {
        checkNFTAccess()
      }, CONFIG.NFT_CHECK_DELAY)
      
      return () => clearTimeout(timer)
    }
  }, [userFriendlyAddress, hasCheckedOnce, isCheckingNFTs, checkNFTAccess])

  useEffect(() => {
    if (!userFriendlyAddress) {
      setHasNFTAccess(false)
      setUserNFTs([])
      setHasCheckedOnce(false)
    }
  }, [userFriendlyAddress])

  return {
    hasNFTAccess,
    userNFTs,
    isCheckingNFTs,
    checkNFTAccess
  }
} 