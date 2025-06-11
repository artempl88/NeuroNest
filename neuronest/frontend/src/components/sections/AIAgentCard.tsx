import React from 'react'
import { motion } from 'framer-motion'
import { ExternalLink } from 'lucide-react'
import type { AIAgentCardProps } from '../../types'

export const AIAgentCard: React.FC<AIAgentCardProps> = ({ agent, index, onExecute }) => {
  return (
    <motion.div
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
            onClick={() => onExecute(agent.name, agent.price)}
          >
            <span>EXECUTE</span>
            <ExternalLink className="w-3 h-3" />
          </button>
        </div>
      </div>
    </motion.div>
  )
} 