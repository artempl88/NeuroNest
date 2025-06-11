import React, { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'

interface Node {
  x: number
  y: number
  vx: number
  vy: number
  connections: number[]
}

export function NeuralNetwork() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const nodesRef = useRef<Node[]>([])
  const animationFrameRef = useRef<number>()

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Размеры канваса
    const resizeCanvas = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }
    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)

    // Создание узлов
    const nodeCount = 15
    const nodes: Node[] = []
    
    for (let i = 0; i < nodeCount; i++) {
      nodes.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        connections: []
      })
    }

    // Создание соединений
    nodes.forEach((node, i) => {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[j].x - node.x
        const dy = nodes[j].y - node.y
        const distance = Math.sqrt(dx * dx + dy * dy)
        
        if (distance < 200 && Math.random() > 0.7) {
          node.connections.push(j)
        }
      }
    })

    nodesRef.current = nodes

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Обновление позиций узлов
      nodes.forEach(node => {
        node.x += node.vx
        node.y += node.vy

        // Отражение от краев
        if (node.x <= 0 || node.x >= canvas.width) node.vx *= -1
        if (node.y <= 0 || node.y >= canvas.height) node.vy *= -1

        // Границы
        node.x = Math.max(0, Math.min(canvas.width, node.x))
        node.y = Math.max(0, Math.min(canvas.height, node.y))
      })

      // Рисование соединений
      nodes.forEach((node, i) => {
        node.connections.forEach(targetIndex => {
          const target = nodes[targetIndex]
          const dx = target.x - node.x
          const dy = target.y - node.y
          const distance = Math.sqrt(dx * dx + dy * dy)
          
          if (distance < 250) {
            const opacity = 1 - distance / 250
            const gradient = ctx.createLinearGradient(node.x, node.y, target.x, target.y)
            gradient.addColorStop(0, `rgba(0, 255, 255, ${opacity * 0.3})`)
            gradient.addColorStop(0.5, `rgba(0, 191, 255, ${opacity * 0.6})`)
            gradient.addColorStop(1, `rgba(0, 255, 255, ${opacity * 0.3})`)

            ctx.strokeStyle = gradient
            ctx.lineWidth = 1
            ctx.setLineDash([5, 10])
            ctx.lineDashOffset = Date.now() * 0.01
            ctx.beginPath()
            ctx.moveTo(node.x, node.y)
            ctx.lineTo(target.x, target.y)
            ctx.stroke()
          }
        })
      })

      // Рисование узлов
      nodes.forEach(node => {
        // Внешнее свечение
        const glowGradient = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, 15)
        glowGradient.addColorStop(0, 'rgba(0, 255, 255, 0.8)')
        glowGradient.addColorStop(0.5, 'rgba(0, 255, 255, 0.3)')
        glowGradient.addColorStop(1, 'rgba(0, 255, 255, 0)')

        ctx.fillStyle = glowGradient
        ctx.beginPath()
        ctx.arc(node.x, node.y, 15, 0, Math.PI * 2)
        ctx.fill()

        // Основной узел
        ctx.fillStyle = '#00FFFF'
        ctx.beginPath()
        ctx.arc(node.x, node.y, 4, 0, Math.PI * 2)
        ctx.fill()

        // Внутренний круг
        ctx.fillStyle = '#0A0A0A'
        ctx.beginPath()
        ctx.arc(node.x, node.y, 2, 0, Math.PI * 2)
        ctx.fill()
      })

      animationFrameRef.current = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener('resize', resizeCanvas)
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 w-full h-full pointer-events-none opacity-30"
      style={{ zIndex: 1 }}
    />
  )
}

export function StaticNeuralNodes() {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none" style={{ zIndex: 0 }}>
      {/* Статические узлы для декорации */}
      <motion.div
        className="neural-node w-3 h-3 absolute top-20 left-20"
        animate={{ scale: [1, 1.2, 1] }}
        transition={{ duration: 2, repeat: Infinity }}
      />
      <motion.div
        className="neural-node w-2 h-2 absolute top-40 right-32"
        animate={{ scale: [1.2, 1, 1.2] }}
        transition={{ duration: 3, repeat: Infinity }}
      />
      <motion.div
        className="neural-node w-4 h-4 absolute bottom-32 left-16"
        animate={{ scale: [1, 1.3, 1] }}
        transition={{ duration: 2.5, repeat: Infinity }}
      />
      <motion.div
        className="neural-node w-2 h-2 absolute bottom-20 right-20"
        animate={{ scale: [1.3, 1, 1.3] }}
        transition={{ duration: 4, repeat: Infinity }}
      />
      
      {/* Статические соединения */}
      <div className="neural-connection absolute top-24 left-24 w-32 transform rotate-45" />
      <div className="neural-connection absolute bottom-36 right-36 w-24 transform -rotate-12" />
    </div>
  )
} 