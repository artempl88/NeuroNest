'use client'

import React, { useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Network,
  Cpu,
  Coins,
  Shield,
  Wallet,
  Cpu as CpuIcon
} from 'lucide-react'
import toast, { Toaster } from 'react-hot-toast'
import { 
  useTonAddress, 
  useTonWallet, 
  useIsConnectionRestored 
} from '@tonconnect/ui-react'

import { NeuralNetwork, StaticNeuralNodes } from '../components/ui/NeuralNetwork'
import { WalletSection } from '../components/sections/WalletSection'
import { AIAgentCard } from '../components/sections/AIAgentCard'
import { ManualNFTCheck } from '../components/sections/ManualNFTCheck'
import { useTelegram } from '../hooks/useTelegram'
import { useNFTAccess } from '../hooks/useNFTAccess'
import { useTonTransaction } from '../hooks/useTonTransaction'
import { AI_AGENTS } from '../constants/agents'
import { ALLOWED_COLLECTIONS } from '../constants/collections'
import { getAccessLevel } from '../utils/access'

export default function HomePage() {
  // ✅ ИСПРАВЛЕНО: Правильное использование хуков на верхнем уровне
  const connectionRestored = useIsConnectionRestored()
  const wallet = useTonWallet()
  const userFriendlyAddress = useTonAddress()
  
  const { user, hapticFeedback, isInTelegram } = useTelegram()
  
  // Используем новые хуки
  const { hasNFTAccess, userNFTs, isCheckingNFTs, checkNFTAccess } = useNFTAccess({
    userFriendlyAddress,
    hapticFeedback
  })
  
  const { executeAgent } = useTonTransaction(hapticFeedback)

  // Обработка ошибок TON Connect
  useEffect(() => {
    const handleTonConnectError = (error: any) => {
      console.error('TON Connect Error:', error)
      hapticFeedback?.notification('error')
      toast.error('Ошибка подключения кошелька. Попробуйте еще раз.')
    }

    window.addEventListener('tonconnect-error', handleTonConnectError)
    
    return () => {
      window.removeEventListener('tonconnect-error', handleTonConnectError)
    }
  }, [hapticFeedback])

  const handleExecuteAgent = async (agentName: string, price: number) => {
    if (!wallet) {
      toast.error('Подключите кошелек')
      return
    }

    if (!hasNFTAccess) {
      toast.error('Требуется NFT доступ')
      return
    }

    try {
      await executeAgent(agentName, price, user?.id?.toString())
    } catch (error) {
      // Ошибка уже обработана в хуке
    }
  }

  const getCurrentAccessLevel = () => {
    return getAccessLevel(userNFTs.length)
  }

  // ✅ ДОБАВЛЕНО: функция для ручной проверки NFT с уведомлениями
  const handleManualNFTCheck = async () => {
    if (!userFriendlyAddress) {
      toast.error('Подключите кошелек для проверки NFT')
      return
    }

    try {
      toast.loading('Проверяем ваши NFT...', { id: 'manual-nft-check' })
      await checkNFTAccess()
      
      // Показываем результат проверки
      setTimeout(() => {
        if (hasNFTAccess) {
          toast.success(`🎉 NFT доступ подтвержден! Уровень: ${getCurrentAccessLevel()}`, { id: 'manual-nft-check' })
        } else {
          toast.error('❌ NFT не найдены в разрешенных коллекциях', { id: 'manual-nft-check' })
        }
      }, 500)
    } catch (error) {
      toast.error('Ошибка проверки NFT', { id: 'manual-nft-check' })
    }
  }

  // Loading скелетон компонент
  const LoadingSkeleton = () => (
    <div className="animate-pulse">
      <div className="h-8 bg-gray-700 rounded mb-4"></div>
      <div className="h-12 bg-gray-700 rounded mb-6"></div>
      <div className="space-y-3">
        <div className="h-4 bg-gray-700 rounded w-3/4"></div>
        <div className="h-4 bg-gray-700 rounded w-1/2"></div>
      </div>
    </div>
  )

  if (!connectionRestored) {
    return <LoadingScreen />
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      <Toaster 
        position="top-center"
        toastOptions={{
          style: {
            background: 'rgba(17, 17, 17, 0.9)',
            color: '#00FFFF',
            border: '1px solid rgba(0, 255, 255, 0.3)',
          },
          duration: 3000, // ✅ ДОБАВЛЕНО: ограничиваем время показа уведомлений
        }}
      />
      
      {/* Нейросетевой фон */}
      <NeuralNetwork />
      <StaticNeuralNodes />
      <div className="neural-grid" />

      <div className="relative z-10">
        {/* Header */}
        <header className="p-6">
          <div className="flex items-center justify-between">
            <motion.div 
              className="flex items-center space-x-4"
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
            >
              <div className="relative">
                <motion.div
                  className="neural-node w-16 h-16 flex items-center justify-center"
                  animate={{ 
                    rotate: [0, 360],
                    scale: [1, 1.1, 1] 
                  }}
                  transition={{ 
                    rotate: { duration: 20, repeat: Infinity, ease: "linear" },
                    scale: { duration: 3, repeat: Infinity, ease: "easeInOut" }
                  }}
                >
                  <Network className="w-8 h-8 text-black relative z-10" />
                </motion.div>
                
                {/* Орбитальные узлы */}
                <motion.div
                  className="neural-node w-3 h-3 absolute -top-1 left-1/2 transform -translate-x-1/2"
                  animate={{ rotate: [0, 360] }}
                  transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
                />
                <motion.div
                  className="neural-node w-2 h-2 absolute top-1/2 -right-1 transform -translate-y-1/2"
                  animate={{ rotate: [0, -360] }}
                  transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
                />
                <motion.div
                  className="neural-node w-3 h-3 absolute -bottom-1 left-1/2 transform -translate-x-1/2"
                  animate={{ rotate: [0, 360] }}
                  transition={{ duration: 12, repeat: Infinity, ease: "linear" }}
                />
                <motion.div
                  className="neural-node w-2 h-2 absolute top-1/2 -left-1 transform -translate-y-1/2"
                  animate={{ rotate: [0, -360] }}
                  transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                />
              </div>
              <div>
                <h1 className="text-3xl font-bold neural-text glitch" data-text="NeuroNest">
                  NeuroNest
                </h1>
                <motion.p 
                  className="text-cyan-400 text-sm font-mono tracking-wider"
                  animate={{ opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  BY NØT PUNKS
                </motion.p>
              </div>
            </motion.div>
            
            {/* Wallet Section */}
            <WalletSection
              wallet={wallet}
              userFriendlyAddress={userFriendlyAddress || ''}
              hasNFTAccess={hasNFTAccess}
              getAccessLevel={getCurrentAccessLevel}
            />
          </div>
        </header>

        {/* Hero Section */}
        <section className="px-6 pt-12 pb-16">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center space-y-8 max-w-4xl mx-auto"
          >
            {/* Main Title */}
            <div className="space-y-6">
              <motion.h1 
                className="text-6xl md:text-7xl font-bold neural-text leading-tight"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, duration: 0.8 }}
              >
                NEURAL AI
                <br />
                <span className="text-4xl md:text-5xl">MARKETPLACE</span>
              </motion.h1>
              
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.6, duration: 0.8 }}
                className="relative"
              >
                <p className="text-xl md:text-2xl text-cyan-300 font-light leading-relaxed max-w-3xl mx-auto">
                  Эксклюзивный маркетплейс AI агентов с NFT-доступом.
                  <br />
                  <span className="text-lg text-cyan-500">Будущее искусственного интеллекта уже здесь.</span>
                </p>
                
                {/* Telegram User Info */}
                {isInTelegram && user && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1 }}
                    className="mt-6 inline-flex items-center space-x-2 cyber-card px-4 py-2"
                  >
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                    <span className="text-cyan-400 text-sm font-mono">
                      Добро пожаловать, {user.first_name}!
                    </span>
                  </motion.div>
                )}
              </motion.div>
            </div>

            {/* Features Grid */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.9, duration: 0.8 }}
              className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16"
            >
              {[
                { 
                  icon: Shield, 
                  title: "NFT ACCESS", 
                  description: "Эксклюзивный доступ через NFT коллекции",
                  color: "from-purple-400 to-blue-500"
                },
                { 
                  icon: CpuIcon, 
                  title: "AI AGENTS", 
                  description: "20+ продвинутых AI агентов",
                  color: "from-cyan-400 to-blue-400"
                },
                { 
                  icon: Coins, 
                  title: "TON PAYMENTS", 
                  description: "Оплата в TON cryptocurrency",
                  color: "from-yellow-400 to-orange-500"
                },
              ].map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1.2 + index * 0.2 }}
                  className="cyber-card p-6 group hover:scale-105 transition-all duration-300"
                >
                  <div className="text-center space-y-4">
                    <div className={`w-16 h-16 mx-auto rounded-full bg-gradient-to-br ${feature.color} p-4 group-hover:shadow-lg group-hover:shadow-cyan-500/25 transition-all`}>
                      <feature.icon className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-xl font-bold text-cyan-300 font-mono tracking-wide">
                      {feature.title}
                    </h3>
                    <p className="text-gray-400 text-sm leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          </motion.div>
        </section>

        {/* AI Agents Section */}
        {wallet && hasNFTAccess && (
          <motion.section
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.5 }}
            className="px-6 pb-16"
          >
            <div className="max-w-6xl mx-auto">
              <div className="flex items-center justify-between mb-8">
                <h2 className="text-3xl font-bold neural-text font-mono">
                  AI AGENTS
                </h2>
                <div className="flex items-center space-x-2 text-cyan-400 text-sm font-mono">
                  <span>ACCESS LEVEL:</span>
                  <span className="bg-cyan-400/20 px-2 py-1 rounded uppercase">
                    {getCurrentAccessLevel()}
                  </span>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {AI_AGENTS.map((agent, index) => (
                  <AIAgentCard
                    key={agent.name}
                    agent={agent}
                    index={index}
                    onExecute={handleExecuteAgent}
                  />
                ))}
              </div>
            </div>
          </motion.section>
        )}

        {/* ✅ ИСПРАВЛЕНО: Используем новый компонент ManualNFTCheck */}
        {wallet && !hasNFTAccess && (
          <ManualNFTCheck 
            isCheckingNFTs={isCheckingNFTs}
            onCheckNFT={handleManualNFTCheck}
            userFriendlyAddress={userFriendlyAddress}
          />
        )}

        {/* No Wallet Connected */}
        {!wallet && (
          <motion.section
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5 }}
            className="px-6 pt-8"
          >
            <div className="max-w-2xl mx-auto cyber-card p-8 text-center">
              <div className="neural-node w-20 h-20 flex items-center justify-center mx-auto mb-6">
                <Wallet className="w-10 h-10 text-black" />
              </div>
              <h3 className="text-2xl font-bold neural-text mb-4 font-mono">
                CONNECT WALLET
              </h3>
              <p className="text-gray-300 mb-6 leading-relaxed">
                Подключите TON кошелек для доступа к эксклюзивным AI агентам
              </p>
            </div>
          </motion.section>
        )}
      </div>
    </div>
  )
}

function LoadingScreen() {
  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      <NeuralNetwork />
      <div className="neural-grid" />
      
      <motion.div
        className="text-center space-y-8 relative z-10"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <motion.div
          className="relative mx-auto"
          animate={{ 
            rotate: [0, 360],
            scale: [1, 1.1, 1] 
          }}
          transition={{ 
            rotate: { duration: 3, repeat: Infinity, ease: "linear" },
            scale: { duration: 2, repeat: Infinity, ease: "easeInOut" }
          }}
        >
          <div className="neural-node w-24 h-24 flex items-center justify-center">
            <Network className="w-12 h-12 text-black" />
          </div>
          
          {/* Орбитальные узлы */}
          {[0, 90, 180, 270].map((rotation, index) => (
            <motion.div
              key={index}
              className="neural-node w-4 h-4 absolute"
              style={{
                top: '50%',
                left: '50%',
                transformOrigin: '50% 50%',
              }}
              animate={{ 
                rotate: [rotation, rotation + 360],
                x: -8,
                y: -40
              }}
              transition={{ 
                rotate: { duration: 4, repeat: Infinity, ease: "linear" },
              }}
            />
          ))}
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="space-y-4"
        >
          <h2 className="text-4xl font-bold neural-text font-mono">
            INITIALIZING
          </h2>
          <div className="flex items-center justify-center space-x-2">
            <span className="text-cyan-400 font-mono">TON CONNECTION</span>
            <motion.div
              animate={{ opacity: [0, 1, 0] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="w-2 h-2 bg-cyan-400 rounded-full"
            />
            <motion.div
              animate={{ opacity: [0, 1, 0] }}
              transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
              className="w-2 h-2 bg-cyan-400 rounded-full"
            />
            <motion.div
              animate={{ opacity: [0, 1, 0] }}
              transition={{ duration: 1.5, repeat: Infinity, delay: 0.4 }}
              className="w-2 h-2 bg-cyan-400 rounded-full"
            />
          </div>
        </motion.div>
      </motion.div>
    </div>
  )
} 