import React from 'react'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { TonConnectProvider } from '../components/providers/TonConnectProvider'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'NeuroNest - Neural AI Marketplace',
  description: 'Эксклюзивный маркетплейс AI агентов с NFT-доступом и крипто-платежами в TON',
  other: {
    'telegram-web-app-title': 'NeuroNest',
    'telegram-web-app-description': 'Neural AI Marketplace',
    'telegram-web-app-header-color': '#000000',
    'telegram-web-app-bg-color': '#000000',
  }
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru">
      <head>
        <script src="https://telegram.org/js/telegram-web-app.js" defer />
        <script src="https://unpkg.com/web-animations-js@latest/web-animations.min.js" defer />
      </head>
      <body className={inter.className}>
        <TonConnectProvider>
          {children}
        </TonConnectProvider>
      </body>
    </html>
  )
} 