import { motion } from 'framer-motion'

interface SkeletonProps {
  className?: string
  height?: string
  width?: string
}

export function Skeleton({ className = '', height = 'h-4', width = 'w-full' }: SkeletonProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className={`
        ${height} ${width} bg-gray-800 rounded
        animate-pulse ${className}
      `}
    />
  )
}

interface PulseLoaderProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function PulseLoader({ size = 'md', className = '' }: PulseLoaderProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  }

  return (
    <motion.div
      animate={{
        scale: [1, 1.1, 1],
        opacity: [1, 0.8, 1]
      }}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: "easeInOut"
      }}
      className={`
        ${sizeClasses[size]} bg-blue-600 rounded-full
        shadow-lg shadow-blue-600/25 ${className}
      `}
    />
  )
}

interface DotsLoaderProps {
  className?: string
}

export function DotsLoader({ className = '' }: DotsLoaderProps) {
  return (
    <div className={`flex space-x-1 ${className}`}>
      {[0, 1, 2].map((index) => (
        <motion.div
          key={index}
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.5, 1, 0.5]
          }}
          transition={{
            duration: 1.2,
            repeat: Infinity,
            delay: index * 0.2,
            ease: "easeInOut"
          }}
          className="w-2 h-2 bg-blue-500 rounded-full"
        />
      ))}
    </div>
  )
}

interface ProgressBarProps {
  progress: number
  stage: string
  className?: string
}

export function ProgressBar({ progress, stage, className = '' }: ProgressBarProps) {
  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex justify-between items-center text-sm">
        <span className="text-gray-300">{stage}</span>
        <span className="text-gray-500">{Math.round(progress)}%</span>
      </div>
      
      <div className="w-full bg-gray-800 rounded-full h-2 overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="h-full bg-gradient-to-r from-blue-500 to-purple-600 rounded-full"
        />
      </div>
    </div>
  )
}

interface StageIndicatorProps {
  stages: Array<{ name: string; status: 'pending' | 'active' | 'completed' }>
  currentStage: number
}

export function StageIndicator({ stages, currentStage }: StageIndicatorProps) {
  return (
    <div className="flex items-center space-x-4">
      {stages.map((stage, index) => (
        <div key={stage.name} className="flex items-center">
          <motion.div
            animate={{
              scale: stage.status === 'active' ? [1, 1.1, 1] : 1,
              opacity: stage.status === 'completed' ? 1 : 0.5
            }}
            transition={{
              scale: { duration: 1, repeat: stage.status === 'active' ? Infinity : 0 },
              opacity: { duration: 0.3 }
            }}
            className={`
              w-8 h-8 rounded-full flex items-center justify-center
              border-2 transition-all duration-300
              ${stage.status === 'completed' 
                ? 'bg-green-600 border-green-600' 
                : stage.status === 'active'
                ? 'bg-blue-600 border-blue-600'
                : 'bg-gray-800 border-gray-700'
              }
            `}
          >
            {stage.status === 'completed' && (
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            )}
            {stage.status === 'active' && (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                className="w-3 h-3 bg-white rounded-full"
              />
            )}
          </motion.div>
          
          <span className={`
            text-xs font-medium ml-2
            ${stage.status === 'completed' ? 'text-green-500' : 
              stage.status === 'active' ? 'text-blue-500' : 'text-gray-500'}
          `}
          >
            {stage.name}
          </span>
          
          {index < stages.length - 1 && (
            <div className={`
              w-8 h-0.5 mx-2
              ${stage.status === 'completed' ? 'bg-green-600' : 'bg-gray-700'}
            `} />
          )}
        </div>
      ))}
    </div>
  )
}
