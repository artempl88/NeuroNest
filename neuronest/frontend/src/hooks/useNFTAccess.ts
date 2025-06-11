import { useState, useEffect, useCallback } from 'react'
import toast from 'react-hot-toast'
import { CONFIG } from '../constants/config'
import type { UseNFTAccessProps, UseNFTAccessReturn, NFT, NFTAccessData } from '../types'

export const useNFTAccess = ({ userFriendlyAddress, hapticFeedback }: UseNFTAccessProps): UseNFTAccessReturn => {
  const [hasNFTAccess, setHasNFTAccess] = useState(false)
  const [userNFTs, setUserNFTs] = useState<NFT[]>([])
  const [isCheckingNFTs, setIsCheckingNFTs] = useState(false)

  const checkNFTAccess = useCallback(async () => {
    if (!userFriendlyAddress) return

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
      
      if (nftData.has_access) {
        hapticFeedback?.notification('success')
        toast.success(`🎉 NFT доступ подтвержден! Уровень: ${nftData.access_level}`)
      } else {
        toast.error('❌ NFT не найдены в разрешенных коллекциях')
      }
      
    } catch (error) {
      console.error('Ошибка проверки NFT:', error)
      handleNFTError(error)
    } finally {
      setIsCheckingNFTs(false)
    }
  }, [userFriendlyAddress, hapticFeedback])

  const handleNFTError = useCallback((error: any) => {
    if (error instanceof TypeError && error.message.includes('NetworkError')) {
      toast.error('Сервер недоступен. Проверьте подключение.')
    } else {
      toast.error('Ошибка проверки NFT коллекций')
    }
    
    hapticFeedback?.notification('error')
    
    // Fallback к демо режиму
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
    toast.success('🔄 Демо режим активирован')
  }, [hapticFeedback])

  // ✅ ИСПРАВЛЕНО: Правильные зависимости и очистка таймера
  useEffect(() => {
    if (userFriendlyAddress && !isCheckingNFTs) {
      const timer = setTimeout(() => {
        checkNFTAccess()
      }, CONFIG.NFT_CHECK_DELAY)
      
      return () => clearTimeout(timer)
    }
  }, [userFriendlyAddress, isCheckingNFTs, checkNFTAccess])

  return {
    hasNFTAccess,
    userNFTs,
    isCheckingNFTs,
    checkNFTAccess
  }
} 