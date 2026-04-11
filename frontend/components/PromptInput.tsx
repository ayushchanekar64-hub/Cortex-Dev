import { useState } from 'react'
import { motion } from 'framer-motion'
import { Send, Square, Sparkles } from 'lucide-react'

interface PromptInputProps {
  value: string
  onChange: (value: string) => void
  onGenerate: (val?: string) => void
  onStop: () => void
  isGenerating: boolean
  placeholder?: string
}

export default function PromptInput({
  value,
  onChange,
  onGenerate,
  onStop,
  isGenerating,
  placeholder = "Describe your project idea..."
}: PromptInputProps) {
  const [isFocused, setIsFocused] = useState(false)

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (!isGenerating && value.trim()) {
        onGenerate(value)
        onChange('')
      }
    }
  }

  return (
    <div className="relative group flex flex-col space-y-2">
      <div
        className={`
          relative rounded-2xl border transition-all duration-300 flex flex-col overflow-hidden
          ${isFocused 
            ? 'border-indigo-500/50 bg-indigo-500/[0.03] shadow-[0_0_20px_rgba(99,102,241,0.05)]' 
            : 'border-white/5 bg-white/[0.02]'}
          ${isGenerating ? 'border-indigo-500/30' : ''}
        `}
      >
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={placeholder}
          rows={3}
          className={`
            w-full px-6 py-5 bg-transparent text-slate-200 
            placeholder-slate-600 border-0 outline-none resize-none
            text-[17px] leading-relaxed transition-all duration-300
            ${isGenerating ? 'opacity-50' : ''}
          `}
        />
        
        <div className="absolute right-3 bottom-3 flex items-center space-x-2">
          {isGenerating ? (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={onStop}
              className="p-2 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl hover:bg-red-500/20 transition-all"
            >
              <Square className="w-4 h-4 fill-current" />
            </motion.button>
          ) : (
            <motion.button
              whileHover={{ scale: 1.05, backgroundColor: 'rgba(99, 102, 241, 1)' }}
              whileTap={{ scale: 0.95 }}
              onClick={() => {
                if (value.trim()) {
                  onGenerate(value)
                  onChange('')
                }
              }}
              disabled={!value.trim()}
              className={`p-2.5 rounded-xl transition-all shadow-lg ${
                value.trim() 
                ? 'bg-indigo-600 text-white shadow-indigo-500/20' 
                : 'bg-white/5 text-slate-600'
              }`}
            >
              <Send className="w-4 h-4" />
            </motion.button>
          )}
        </div>
      </div>
      <div className="flex items-center justify-between px-2 text-[10px] text-slate-500 font-bold uppercase tracking-widest">
        <div className="flex items-center space-x-1">
          <Sparkles className="w-3 h-3 text-indigo-400" />
          <span>AI Synthesis Ready</span>
        </div>
        <span>{value.length} Chars</span>
      </div>
    </div>
  )
}
