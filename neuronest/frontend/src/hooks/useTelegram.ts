import { useEffect, useState } from 'react'

interface TelegramUser {
  id: number
  first_name: string
  last_name?: string
  username?: string
  language_code?: string
  is_premium?: boolean
}

interface WebApp {
  initData: string
  initDataUnsafe: {
    user?: TelegramUser
    start_param?: string
  }
  version: string
  platform: string
  colorScheme: 'light' | 'dark'
  themeParams: {
    link_color: string
    button_color: string
    button_text_color: string
    secondary_bg_color: string
  }
  isExpanded: boolean
  viewportHeight: number
  viewportStableHeight: number
  ready: () => void
  expand: () => void
  close: () => void
  MainButton: {
    text: string
    color: string
    textColor: string
    isVisible: boolean
    isActive: boolean
    readonly isProgressVisible: boolean
    setText: (text: string) => void
    onClick: (callback: () => void) => void
    offClick: (callback: () => void) => void
    show: () => void
    hide: () => void
    enable: () => void
    disable: () => void
    showProgress: (leaveActive?: boolean) => void
    hideProgress: () => void
    setParams: (params: {
      text?: string
      color?: string
      text_color?: string
      is_active?: boolean
      is_visible?: boolean
    }) => void
  }
  BackButton: {
    isVisible: boolean
    onClick: (callback: () => void) => void
    offClick: (callback: () => void) => void
    show: () => void
    hide: () => void
  }
  HapticFeedback: {
    impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void
    notificationOccurred: (type: 'error' | 'success' | 'warning') => void
    selectionChanged: () => void
  }
  showPopup: (params: {
    title?: string
    message: string
    buttons?: Array<{
      id?: string
      type?: 'default' | 'ok' | 'close' | 'cancel' | 'destructive'
      text: string
    }>
  }, callback?: (buttonId: string) => void) => void
  showAlert: (message: string, callback?: () => void) => void
  showConfirm: (message: string, callback?: (confirmed: boolean) => void) => void
  showScanQrPopup: (params: {
    text?: string
  }, callback?: (text: string) => boolean) => void
  closeScanQrPopup: () => void
  sendData: (data: string) => void
  switchInlineQuery: (query: string, choose_chat_types?: string[]) => void
  openLink: (url: string, options?: { try_instant_view?: boolean }) => void
  openTelegramLink: (url: string) => void
  openInvoice: (url: string, callback?: (status: string) => void) => void
}

declare global {
  interface Window {
    Telegram?: {
      WebApp: WebApp
    }
  }
}

export function useTelegram() {
  const [isReady, setIsReady] = useState(false)
  const [user, setUser] = useState<TelegramUser | null>(null)
  const [webApp, setWebApp] = useState<WebApp | null>(null)

  useEffect(() => {
    // Проверяем, что мы внутри Telegram
    if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
      const tg = window.Telegram.WebApp
      setWebApp(tg)
      
      // Инициализируем WebApp
      tg.ready()
      tg.expand()
      
      // Получаем данные пользователя
      if (tg.initDataUnsafe.user) {
        setUser(tg.initDataUnsafe.user)
      }
      
      setIsReady(true)
      
      // Настраиваем тему
      document.documentElement.style.setProperty('--tg-theme-bg-color', tg.themeParams.secondary_bg_color || '#000000')
      document.documentElement.style.setProperty('--tg-theme-button-color', tg.themeParams.button_color || '#00FFFF')
      document.documentElement.style.setProperty('--tg-theme-button-text-color', tg.themeParams.button_text_color || '#000000')
      document.documentElement.style.setProperty('--tg-theme-link-color', tg.themeParams.link_color || '#00FFFF')
    } else {
      // Фаллбек для разработки вне Telegram
      console.log('🔧 Development mode: Telegram WebApp not available')
      setIsReady(true)
      // Мок пользователь для разработки
      setUser({
        id: 123456789,
        first_name: 'Test',
        last_name: 'User',
        username: 'testuser',
        language_code: 'ru',
        is_premium: false
      })
    }
  }, [])

  const hapticFeedback = {
    impact: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft' = 'medium') => {
      webApp?.HapticFeedback.impactOccurred(style)
    },
    notification: (type: 'error' | 'success' | 'warning') => {
      webApp?.HapticFeedback.notificationOccurred(type)
    },
    selection: () => {
      webApp?.HapticFeedback.selectionChanged()
    }
  }

  const showAlert = (message: string, callback?: () => void) => {
    if (webApp) {
      webApp.showAlert(message, callback)
    } else {
      alert(message)
      callback?.()
    }
  }

  const showConfirm = (message: string, callback?: (confirmed: boolean) => void) => {
    if (webApp) {
      webApp.showConfirm(message, callback)
    } else {
      const result = confirm(message)
      callback?.(result)
    }
  }

  const close = () => {
    webApp?.close()
  }

  const openLink = (url: string) => {
    if (webApp) {
      webApp.openLink(url)
    } else {
      window.open(url, '_blank')
    }
  }

  return {
    isReady,
    user,
    webApp,
    hapticFeedback,
    showAlert,
    showConfirm,
    close,
    openLink,
    isInTelegram: !!webApp,
    platform: webApp?.platform || 'unknown',
    colorScheme: webApp?.colorScheme || 'dark'
  }
} 