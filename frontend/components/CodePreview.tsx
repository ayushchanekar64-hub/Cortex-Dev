import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Copy, Download, ExternalLink } from 'lucide-react'
import { GeneratedFile } from '../types'

interface CodePreviewProps {
  file: GeneratedFile | null
  files: GeneratedFile[]
  fontSize?: string
}

export default function CodePreview({ file, files, fontSize = '14px' }: CodePreviewProps) {
  const [copied, setCopied] = useState(false)

  const getLanguageClass = (language: string) => {
    const langMap: { [key: string]: string } = {
      'typescript': 'language-typescript',
      'javascript': 'language-javascript',
      'python': 'language-python',
      'json': 'language-json',
      'html': 'language-html',
      'css': 'language-css',
      'jsx': 'language-jsx',
      'tsx': 'language-tsx',
      'text': 'language-text'
    }
    return langMap[language] || 'language-text'
  }

  const handleCopy = async () => {
    if (file?.content) {
      try {
        await navigator.clipboard.writeText(file.content)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      } catch (err) {
        console.error('Failed to copy:', err)
      }
    }
  }

  const handleDownload = () => {
    if (file) {
      const blob = new Blob([file.content], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = file.name
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }
  }

  const handleDownloadAll = () => {
    files.forEach(file => {
      setTimeout(() => {
        const blob = new Blob([file.content], { type: 'text/plain' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = file.name
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      }, files.indexOf(file) * 100)
    })
  }

  useEffect(() => {
    const loadPrism = async () => {
      try {
        const Prism = await import('prismjs')
        await import('prismjs/components/prism-typescript')
        await import('prismjs/components/prism-javascript')
        await import('prismjs/components/prism-python')
        await import('prismjs/components/prism-json')
        Prism.highlightAll()
      } catch (err) {
        console.log('Prism.js not loaded, using plain text')
      }
    }

    if (file) {
      loadPrism()
    }
  }, [file])

  return (
    <div className="h-full flex flex-col bg-transparent relative">
      {/* 1. Futuristic Header */}
      <div className="px-6 h-12 border-b border-white/5 flex items-center justify-between bg-white/[0.01]">
        <div className="flex items-center gap-4">
          <div className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse shadow-[0_0_8px_indigo]" />
          <span className="text-sm font-bold tracking-widest text-slate-300 uppercase">
            {file ? file.name : 'Console Idle'}
          </span>
        </div>

        {file && (
          <div className="flex items-center gap-1.5">
            {[
              { icon: Copy, title: 'Sync to Clipboard', action: handleCopy, id: 'copy' },
              { icon: Download, title: 'Materialize Locally', action: handleDownload, id: 'dl' },
              { icon: ExternalLink, title: 'Sync Whole Cluster', action: handleDownloadAll, id: 'dl-all' }
            ].map(btn => (
              <motion.button
                key={btn.id}
                whileHover={{ scale: 1.05, backgroundColor: 'rgba(99, 102, 241, 0.1)' }}
                whileTap={{ scale: 0.95 }}
                onClick={btn.action}
                className="p-2 text-slate-500 hover:text-indigo-400 rounded-lg transition-all border border-transparent hover:border-indigo-500/20"
                title={btn.title}
              >
                <btn.icon className="w-4 h-4" />
              </motion.button>
            ))}
          </div>
        )}
      </div>

      <div className="flex-1 flex flex-col overflow-hidden">
        {!file ? (
          <div className="h-full flex items-center justify-center text-slate-600">
            <div className="text-center">
              <div className="w-20 h-20 bg-white/[0.02] border border-white/5 rounded-3xl flex items-center justify-center mb-6 mx-auto">
                <div className="text-3xl text-indigo-500/20">{`</>`}</div>
              </div>
              <p className="text-[10px] font-bold tracking-[0.2em] uppercase">No Module Selected</p>
            </div>
          </div>
        ) : (
          <div className="h-full flex flex-col">
            {/* Breadcrumb Path */}
            <div className="px-6 py-2 bg-black/20 border-b border-white/5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-[10px] font-mono text-slate-500">
                  <span className="opacity-50 tracking-tighter">PROJECT_ROOT /</span>
                  <span className="text-indigo-400 font-bold">{file.path}</span>
                </div>
                {file.language && (
                  <div className="flex items-center gap-1.5 px-2 py-0.5 bg-emerald-500/10 border border-emerald-500/20 rounded-md">
                    <div className="w-1 h-1 bg-emerald-400 rounded-full" />
                    <span className="text-[9px] font-bold text-emerald-400 uppercase tracking-widest">{file.language}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Code Field */}
            <div className="flex-1 overflow-auto custom-scrollbar bg-black/40">
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
                className="p-6 h-full"
              >
                <div className="bg-[#0f1115]/50 rounded-2xl border border-white/5 p-4 h-full overflow-auto">
                  <pre className="p-8 pt-4 m-0 overflow-auto custom-scrollbar h-full selection:bg-indigo-500/30" style={{ fontSize }}>
                    <code className={`${getLanguageClass(file.language)} font-mono leading-relaxed block`}>
                      {file.content}
                    </code>
                  </pre>
                </div>
              </motion.div>
            </div>
          </div>
        )}
      </div>

      {/* Sync Notification */}
      <AnimatePresence>
        {copied && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="absolute bottom-4 right-4 bg-indigo-600 text-white px-5 py-2.5 rounded-2xl shadow-[0_0_30px_rgba(79,70,229,0.5)] text-xs font-bold tracking-widest uppercase z-[100]"
          >
            Neural Buffer Synced
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
