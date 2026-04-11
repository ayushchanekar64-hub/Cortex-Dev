import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Terminal, Info, CheckCircle, AlertTriangle, X, Zap } from 'lucide-react'
import { LogEntry } from '../types'
import { DotsLoader } from './LoadingStates'

interface LogsSectionProps {
  logs: LogEntry[]
}

export default function LogsSection({ logs }: LogsSectionProps) {
  const logsEndRef = useRef<HTMLDivElement>(null)
  const [isExpanded, setIsExpanded] = useState(true)

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  const getLogIcon = (level: LogEntry['level']) => {
    switch (level) {
      case 'info':
        return <Info className="w-3 h-3 text-indigo-400" />
      case 'success':
        return <CheckCircle className="w-3 h-3 text-emerald-400" />
      case 'warning':
        return <AlertTriangle className="w-3 h-3 text-amber-400" />
      case 'error':
        return <Zap className="w-3 h-3 text-rose-500" />
    }
  }

  const getLogLevelClass = (level: LogEntry['level']) => {
    switch (level) {
      case 'info':
        return 'text-indigo-300'
      case 'success':
        return 'text-emerald-400'
      case 'warning':
        return 'text-amber-300'
      case 'error':
        return 'text-rose-400'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
    })
  }

  return (
    <div className="h-full flex flex-col bg-transparent font-mono">
      <div className="flex-1 overflow-hidden">
        <div className="h-full overflow-y-auto custom-scrollbar p-6 space-y-3">
          {logs.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-700 opacity-20">
              <Terminal className="w-16 h-16 mb-4" />
              <p className="text-[10px] font-bold tracking-[0.3em] uppercase">Neural Stream Offline</p>
            </div>
          ) : (
            <AnimatePresence mode="popLayout">
              {logs.map((log, index) => (
                <motion.div
                  key={log.id}
                  initial={{ opacity: 0, x: -10, scale: 0.98 }}
                  animate={{ opacity: 1, x: 0, scale: 1 }}
                  transition={{ duration: 0.2 }}
                  className="group flex items-start gap-5 p-4 rounded-xl bg-white/[0.01] border border-white/[0.03] hover:bg-white/[0.03] transition-all"
                >
                  <span className="text-xs text-slate-600 font-bold shrink-0 mt-0.5">
                    [{formatTimestamp(log.timestamp)}]
                  </span>

                  <div className="mt-1 shrink-0">
                    {getLogIcon(log.level)}
                  </div>

                  <span className={`flex-1 text-[13px] leading-relaxed tracking-tight ${getLogLevelClass(log.level)} font-medium`}>
                    <span className="opacity-50 font-bold text-[10px] mr-3">SYS_MSG //</span>
                    {log.message}
                    {index === logs.length - 1 && (
                      <motion.span
                        animate={{ opacity: [1, 0, 1] }}
                        transition={{ duration: 0.8, repeat: Infinity }}
                        className="inline-block w-1.5 h-3 bg-indigo-500 ml-2 align-middle shadow-[0_0_8px_indigo]"
                      />
                    )}
                  </span>
                </motion.div>
              ))}
              <div ref={logsEndRef} />
            </AnimatePresence>
          )}
        </div>
      </div>

      {logs.length > 0 && (
        <div className="px-6 py-2 border-t border-white/5 bg-black/20 flex items-center justify-between">
          <div className="flex items-center gap-6">
            {[
              { label: 'Total', count: logs.length, color: 'bg-indigo-500' },
              { label: 'Neural', count: logs.filter(l => l.level === 'success').length, color: 'bg-emerald-500' }
            ].map(stat => (
              <div key={stat.label} className="flex items-center gap-2">
                <div className={`w-1 h-1 ${stat.color} rounded-full`} />
                <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">{stat.label}: {stat.count}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
