'use client'

import React from 'react'

interface Props {
  children: React.ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="cyber-card p-8 text-center max-w-md">
            <h2 className="text-2xl font-bold text-red-400 mb-4">
              Произошла ошибка
            </h2>
            <p className="text-gray-300 mb-4">
              {this.state.error?.message || 'Неизвестная ошибка'}
            </p>
            <button 
              className="cyber-button px-6 py-2"
              onClick={() => window.location.reload()}
            >
              Перезагрузить
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
} 