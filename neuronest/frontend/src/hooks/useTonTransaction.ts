import { useState } from 'react'
import { useTonConnectUI } from '@tonconnect/ui-react'
import toast from 'react-hot-toast'

export const useTonTransaction = (hapticFeedback: any) => {
  const [tonConnectUI] = useTonConnectUI()
  const [isProcessing, setIsProcessing] = useState(false)

  const executeAgent = async (agentName: string, price: number, userId?: string) => {
    if (!tonConnectUI) {
      toast.error('TON Connect не готов. Попробуйте позже.')
      return
    }

    setIsProcessing(true)
    try {
      hapticFeedback.impact('medium')
      
      const transaction = {
        validUntil: Math.floor(Date.now() / 1000) + 60,
        messages: [{
          address: "EQBfbkxNqgzQQm_GqL4zQGLm2N6_r-5rG_3k4l__NF8qf",
          amount: (price * 1000000000).toString(),
          payload: btoa(JSON.stringify({
            type: 'agent_execution',
            agent: agentName,
            user: userId || 'anonymous'
          }))
        }]
      }

      toast.loading('Выполнение транзакции...', { id: 'tx' })
      
      const result = await tonConnectUI.sendTransaction(transaction)
      
      toast.success(`✅ Агент ${agentName} запущен!`, { id: 'tx' })
      hapticFeedback.notification('success')
      
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
    } else {
      toast.error('Ошибка выполнения транзакции', { id: 'tx' })
    }
    
    hapticFeedback.notification('error')
  }

  return { executeAgent, isProcessing }
} 