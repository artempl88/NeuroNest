'use client'

import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Bot, 
  Shield, 
  Coins, 
  Users,
  Star,
  TrendingUp,
  Rocket,
  Zap,
  Network,
  Cpu,
  Wallet,
  ExternalLink
} from 'lucide-react'
import toast, { Toaster } from 'react-hot-toast'
import { 
  TonConnectButton, 
  useTonAddress, 
  useTonWallet, 
  useTonConnectUI,
  useIsConnectionRestored 
} from '@tonconnect/ui-react'
import { NeuralNetwork, StaticNeuralNodes } from '../components/ui/NeuralNetwork'
import { useTelegram } from '../hooks/useTelegram'

// Мок данные для NFT коллекций
const ALLOWED_COLLECTIONS = [
  {
    address: 'EQCGbQyAJxxMsYQWLCklkXQq4fkIBK3kz3GA1TkFJyUR9nTH',
    name: 'NeuroNest Access Collection',
    description: 'Официальная NFT коллекция для доступа к NeuroNest'
  }
]

export default function HomePage() {
  // Безопасная инициализация TON Connect хуков
  let connectionRestored = true
  let wallet = null
  let userFriendlyAddress = null
  let tonConnectUI = null

  try {
    connectionRestored = useIsConnectionRestored()
    wallet = useTonWallet()
    userFriendlyAddress = useTonAddress()
    const [tcUI] = useTonConnectUI()
    tonConnectUI = tcUI
  } catch (error) {
    console.warn('TON Connect not available:', error)
  }
  
  const [hasNFTAccess, setHasNFTAccess] = useState(false)
  const [userNFTs, setUserNFTs] = useState<any[]>([])
  const [isCheckingNFTs, setIsCheckingNFTs] = useState(false)
  
  const { user, hapticFeedback, showAlert, isInTelegram } = useTelegram()

  // Проверка NFT при подключении кошелька
  useEffect(() => {
    if (wallet && userFriendlyAddress && !isCheckingNFTs) {
      // Добавляем небольшую задержку для стабилизации подключения
      const timer = setTimeout(() => {
        checkNFTAccess()
      }, 1000)
      
      return () => clearTimeout(timer)
    }
  }, [wallet, userFriendlyAddress])

  // Обработка ошибок TON Connect
  useEffect(() => {
    const handleTonConnectError = (error: any) => {
      console.error('TON Connect Error:', error)
      hapticFeedback.notification('error')
      toast.error('Ошибка подключения кошелька. Попробуйте еще раз.')
    }

    window.addEventListener('tonconnect-error', handleTonConnectError)
    
    return () => {
      window.removeEventListener('tonconnect-error', handleTonConnectError)
    }
  }, [])

  const checkNFTAccess = async () => {
    if (!userFriendlyAddress) return

    setIsCheckingNFTs(true)
    try {
      // Вызываем реальный API для проверки NFT
      const response = await fetch('http://localhost:8000/api/v1/wallet/check-nft', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          wallet_address: userFriendlyAddress
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const nftData = await response.json()
      
      setUserNFTs(nftData.nfts || [])
      setHasNFTAccess(nftData.has_access || false)
      
      if (nftData.has_access) {
        hapticFeedback.notification('success')
        toast.success(`🎉 NFT доступ подтвержден! Уровень: ${nftData.access_level}`)
      } else {
        toast.error('❌ NFT не найдены в разрешенных коллекциях')
      }
      
      // Показываем дополнительную информацию если есть fallback режим
      if (nftData.fallback_mode) {
        console.log('Работаем в fallback режиме (TON API недоступно)')
      }
      
    } catch (error) {
      console.error('Ошибка проверки NFT:', error)
      
      // Более детальная обработка ошибок
      if (error instanceof TypeError && error.message.includes('NetworkError')) {
        toast.error('Сервер недоступен. Проверьте подключение.')
      } else {
        toast.error('Ошибка проверки NFT коллекций')
      }
      
      hapticFeedback.notification('error')
      
      // Fallback к демо режиму
      const mockNFTs = [
        {
          collection: ALLOWED_COLLECTIONS[0].address,
          tokenId: '1',
          name: 'NeuroNest Access Pass #1 (Demo)',
          image: 'https://via.placeholder.com/300x300/00FFFF/000000?text=NEURONEST',
          verified: true
        }
      ]
      
      setUserNFTs(mockNFTs)
      setHasNFTAccess(true)
      toast.success('🔄 Демо режим активирован')
      
    } finally {
      setIsCheckingNFTs(false)
    }
  }

  const executeAgent = async (agentName: string, price: number) => {
    if (!wallet) {
      toast.error('Подключите кошелек')
      return
    }

    if (!hasNFTAccess) {
      toast.error('Требуется NFT доступ')
      return
    }

    try {
      hapticFeedback.impact('medium')
      
      // Проверяем готовность TON Connect UI
      if (!tonConnectUI) {
        toast.error('TON Connect не готов. Попробуйте позже.')
        return
      }
      
      // Симуляция транзакции в TON
      const transaction = {
        validUntil: Math.floor(Date.now() / 1000) + 60,
        messages: [
          {
            address: "EQBfbkxNqgzQQm_GqL4zQGLm2N6_r-5rG_3k4l__NF8qf", // адрес получателя
            amount: (price * 1000000000).toString(), // в наногрантах
            payload: btoa(JSON.stringify({
              type: 'agent_execution',
              agent: agentName,
              user: user?.id || 'anonymous'
            }))
          }
        ]
      }

      toast.loading('Выполнение транзакции...', { id: 'tx' })
      
      const result = await tonConnectUI.sendTransaction(transaction)
      
      toast.success(`✅ Агент ${agentName} запущен!`, { id: 'tx' })
      hapticFeedback.notification('success')
      
    } catch (error: any) {
      console.error('Ошибка транзакции:', error)
      
      // Специальная обработка ошибок TON Connect
      if (error?.name === 'TonConnectError') {
        toast.error('Транзакция отменена пользователем', { id: 'tx' })
      } else if (error?.message?.includes('User rejected')) {
        toast.error('Транзакция отклонена', { id: 'tx' })
      } else {
        toast.error('Ошибка выполнения транзакции', { id: 'tx' })
      }
      
      hapticFeedback.notification('error')
    }
  }

  const formatAddress = (address: string) => {
    if (!address) return ''
    return `${address.slice(0, 6)}...${address.slice(-6)}`
  }

  const getAccessLevel = () => {
    if (!hasNFTAccess) return 'none'
    if (userNFTs.length >= 10) return 'premium'
    if (userNFTs.length >= 3) return 'advanced'
    return 'basic'
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
                  icon: Cpu, 
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
                    {getAccessLevel()}
                  </span>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                  {
                    name: "CRYPTO ANALYZER",
                    description: "Анализ крипто-портфеля и торговые стратегии",
                    price: 5.0,
                    rating: 95,
                    icon: TrendingUp,
                    category: "FINANCE"
                  },
                  {
                    name: "NFT VALUATOR",
                    description: "Оценка NFT коллекций и прогноз цен",
                    price: 3.0,
                    rating: 88,
                    icon: Shield,
                    category: "FINANCE"
                  },
                  {
                    name: "CODE REVIEWER",
                    description: "Автоматический анализ и ревью кода",
                    price: 2.0,
                    rating: 92,
                    icon: Bot,
                    category: "DEV"
                  }
                ].map((agent, index) => (
                  <motion.div
                    key={agent.name}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1.8 + index * 0.2 }}
                    className="cyber-card p-6 group hover:scale-105 transition-all cursor-pointer"
                  >
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="neural-node w-10 h-10 flex items-center justify-center">
                            <agent.icon className="w-5 h-5 text-black" />
                          </div>
                          <span className="text-xs font-mono text-cyan-400 bg-cyan-400/10 px-2 py-1 rounded">
                            {agent.category}
                          </span>
                        </div>
                        <div className="text-right">
                          <div className="text-xs text-gray-400 font-mono">RATING</div>
                          <div className="text-sm font-bold text-green-400 font-mono">{agent.rating}%</div>
                        </div>
                      </div>
                      
                      <div>
                        <h3 className="text-lg font-bold text-cyan-300 font-mono mb-2">
                          {agent.name}
                        </h3>
                        <p className="text-gray-400 text-sm leading-relaxed">
                          {agent.description}
                        </p>
                      </div>
                      
                      <div className="flex items-center justify-between pt-4 border-t border-gray-700">
                        <span className="text-cyan-400 font-mono font-bold">
                          {agent.price} TON
                        </span>
                        <button 
                          className="cyber-button px-4 py-2 text-sm font-mono flex items-center space-x-2"
                          onClick={() => executeAgent(agent.name, agent.price)}
                        >
                          <span>EXECUTE</span>
                          <ExternalLink className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.section>
        )}

        {/* Welcome Message for New Users */}
        {wallet && !hasNFTAccess && (
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
              
              {isCheckingNFTs && (
                <div className="text-cyan-400 font-mono mb-4">
                  Проверяем ваши NFT...
                </div>
              )}
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button 
                  className="cyber-button px-6 py-3 font-mono font-bold"
                  onClick={checkNFTAccess}
                  disabled={isCheckingNFTs}
                >
                  {isCheckingNFTs ? 'CHECKING...' : 'CHECK NFT'}
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