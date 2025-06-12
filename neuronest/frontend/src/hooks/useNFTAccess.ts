import { useState, useEffect, useCallback } from 'react'
import toast from 'react-hot-toast'
import { CONFIG } from '../constants/config'
import { validateNFTAccessData } from '../utils/validation'
import { isDemoMode, getDemoNFTs } from '../utils/demo'
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
      const response = await fetch(`/api/v1/wallet/check-nft`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ wallet_address: userFriendlyAddress })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const rawData = await response.json()
      const nftData = validateNFTAccessData(rawData)
      
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
      toast.error('Сервер недоступен. Проверьте подключение.')
    } else {
      toast.error('Ошибка проверки NFT коллекций')
    }
    
    hapticFeedback?.notification('error')
    
    // Включать демо только если явно указано
    if (isDemoMode()) {
      setUserNFTs(getDemoNFTs())
      setHasNFTAccess(true)
      toast.success('🔄 Демо режим активирован')
    }
    
    setHasCheckedOnce(true)
  }, [hapticFeedback])

  useEffect(() => {
    let mounted = true
    let timer: NodeJS.Timeout
    
    if (userFriendlyAddress && !isCheckingNFTs && !hasNFTAccess) {
      timer = setTimeout(() => {
        if (mounted) {
          checkNFTAccess()
        }
      }, CONFIG.NFT_CHECK_DELAY)
    }
    
    return () => {
      mounted = false
      if (timer) clearTimeout(timer)
    }
  }, [userFriendlyAddress]) // Убрал лишние зависимости

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