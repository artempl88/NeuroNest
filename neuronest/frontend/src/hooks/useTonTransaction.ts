import { useState } from 'react'
import { useTonConnectUI } from '@tonconnect/ui-react'
import toast from 'react-hot-toast'
import { CONFIG } from '../constants/config'
import type { HapticFeedback, UseTonTransactionReturn } from '../types'

export const useTonTransaction = (hapticFeedback: HapticFeedback | null): UseTonTransactionReturn => {
  const [tonConnectUI] = useTonConnectUI()
  const [isProcessing, setIsProcessing] = useState(false)

  const executeAgent = async (agentName: string, price: number, userId?: string) => {
    if (!tonConnectUI) {
      toast.error('TON Connect не готов. Попробуйте позже.')
      return
    }

    setIsProcessing(true)
    try {
      hapticFeedback?.impact('medium')
      
      const transaction = {
        validUntil: Math.floor(Date.now() / 1000) + CONFIG.TRANSACTION_TIMEOUT,
        messages: [{
          address: CONFIG.PAYMENT_ADDRESS,
          amount: (price * 1000000000).toString(), // Convert TON to nanotons
          payload: btoa(unescape(encodeURIComponent(JSON.stringify({
            type: 'agent_execution',
            agent: agentName,
            user: userId || 'anonymous',
            timestamp: Date.now()
          }))))
        }]
      }

      toast.loading('Выполнение транзакции...', { id: 'tx' })
      
      const result = await tonConnectUI.sendTransaction(transaction)
      
      toast.success(`✅ Агент ${agentName} запущен!`, { id: 'tx' })
      hapticFeedback?.notification('success')
      
      return result
      
    } catch (error: any) {
      handleTransactionError(error)
      throw error
    } finally {
      setIsProcessing(false)
    }
  }

  const handleTransactionError = (error: any) => {
    console.error('Ошибка транзакции:', error)
    
    if (error?.name === 'TonConnectError' || error?.message?.includes('User rejected')) {
      toast.error('Транзакция отменена пользователем', { id: 'tx' })
    } else if (error?.message?.includes('Insufficient funds')) {
      toast.error('Недостаточно средств для выполнения транзакции', { id: 'tx' })
    } else if (error?.message?.includes('Network')) {
      toast.error('Ошибка сети. Проверьте подключение к интернету', { id: 'tx' })
    } else {
      toast.error('Ошибка выполнения транзакции', { id: 'tx' })
    }
    
    hapticFeedback?.notification('error')
  }

  return { executeAgent, isProcessing }
} 