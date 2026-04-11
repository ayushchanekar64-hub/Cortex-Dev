import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

interface StreamingTextProps {
  text: string
  speed?: number
  className?: string
  onComplete?: () => void
}

export default function StreamingText({ 
  text, 
  speed = 30, 
  className = '',
  onComplete 
}: StreamingTextProps) {
  const [displayedText, setDisplayedText] = useState('')
  const [isComplete, setIsComplete] = useState(false)

  useEffect(() => {
    setDisplayedText('')
    setIsComplete(false)
    
    if (!text) return

    let currentIndex = 0
    const interval = setInterval(() => {
      if (currentIndex < text.length) {
        setDisplayedText(prev => prev + text[currentIndex])
        currentIndex++
      } else {
        clearInterval(interval)
        setIsComplete(true)
        onComplete?.()
      }
    }, speed)

    return () => clearInterval(interval)
  }, [text, speed])

  return (
    <span className={className}>
      {displayedText}
      {!isComplete && (
        <motion.span
          animate={{ opacity: [1, 0.5, 1] }}
          transition={{ duration: 0.8, repeat: Infinity }}
          className="inline-block w-2 h-4 bg-blue-500 ml-1 align-middle"
        />
      )}
    </span>
  )
}
