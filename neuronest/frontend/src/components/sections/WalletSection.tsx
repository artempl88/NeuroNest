import React from 'react'
import { motion } from 'framer-motion'
import { Wallet, Shield } from 'lucide-react'
import { TonConnectButton } from '@tonconnect/ui-react'
import { formatAddress } from '../../utils/access'
import type { WalletSectionProps } from '../../types'

export const WalletSection: React.FC<WalletSectionProps> = ({
  wallet,
  userFriendlyAddress,
  hasNFTAccess,
  getAccessLevel
}) => {
  return (
    <div className="flex items-center space-x-4">
      {wallet && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="cyber-card px-4 py-2 flex items-center space-x-3"
        >
          <div className="flex flex-col items-end">
            <div className="flex items-center space-x-2">
              <Wallet className="w-4 h-4 text-cyan-400" />
              <span className="text-cyan-300 text-sm font-mono">
                {formatAddress(userFriendlyAddress)}
              </span>
            </div>
            {hasNFTAccess && (
              <div className="flex items-center space-x-1 mt-1">
                <Shield className="w-3 h-3 text-green-400" />
                <span className="text-green-400 text-xs font-mono uppercase">
                  {getAccessLevel()} ACCESS
                </span>
              </div>
            )}
          </div>
        </motion.div>
      )}
      
      <div className="cyber-button-wrapper">
        <TonConnectButton className="!bg-gradient-to-r !from-cyan-500 !to-blue-500 !rounded-lg !text-black !font-bold !font-mono" />
      </div>
    </div>
  )
} 