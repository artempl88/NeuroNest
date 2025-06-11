import React from 'react'
import { motion } from 'framer-motion'
import { Shield, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'

interface ManualNFTCheckProps {
  isCheckingNFTs: boolean
  onCheckNFT: () => Promise<void>
  userFriendlyAddress: string | null
}

export const ManualNFTCheck: React.FC<ManualNFTCheckProps> = ({
  isCheckingNFTs,
  onCheckNFT,
  userFriendlyAddress
}) => {
  const handleManualCheck = async () => {
    if (!userFriendlyAddress) {
      toast.error('Подключите кошелек для проверки NFT')
      return
    }

    try {
      toast.loading('Проверяем ваши NFT...', { id: 'nft-check' })
      await onCheckNFT()
      toast.dismiss('nft-check')
    } catch (error) {
      toast.error('Ошибка проверки NFT', { id: 'nft-check' })
    }
  }

  return (
    <motion.section
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.5 }}
      className="px-6 pt-8"
    >
      <div className="max-w-2xl mx-auto cyber-card p-8 text-center">
        <div className="neural-node w-20 h-20 flex items-center justify-center mx-auto mb-6">
          <Shield className="w-10 h-10 text-black" />
        </div>
        <h3 className="text-2xl font-bold neural-text mb-4 font-mono">
          ACCESS REQUIRED
        </h3>
        <p className="text-gray-300 mb-6 leading-relaxed">
          Для доступа к AI агентам необходимо владение NFT из коллекции 
          NeuroNest Access Collection.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button 
            className="cyber-button px-6 py-3 font-mono font-bold flex items-center justify-center space-x-2"
            onClick={handleManualCheck}
            disabled={isCheckingNFTs}
          >
            {isCheckingNFTs ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>CHECKING...</span>
              </>
            ) : (
              <>
                <Shield className="w-4 h-4" />
                <span>CHECK NFT</span>
              </>
            )}
          </button>
          <button 
            className="border border-cyan-400/30 px-6 py-3 font-mono font-bold text-cyan-400 hover:border-cyan-400/60 transition-colors"
            onClick={() => window.open('https://getgems.io/collection/EQCGbQyAJxxMsYQWLCklkXQq4fkIBK3kz3GA1TkFJyUR9nTH', '_blank')}
          >
            GET NFT
          </button>
        </div>
      </div>
    </motion.section>
  )
} 