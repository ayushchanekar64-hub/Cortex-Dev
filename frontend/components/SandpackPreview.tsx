import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Sandpack, 
  SandpackLayout, 
  SandpackCodeEditor, 
  SandpackPreview,
  SandpackFileExplorer,
  useSandpack
} from '@codesandbox/sandpack-react'
import { 
  Loader2, 
  AlertCircle, 
  CheckCircle, 
  RefreshCw,
  Monitor,
  XCircle
} from 'lucide-react'
import { GeneratedFile } from '../types'

interface SandpackPreviewProps {
  files: GeneratedFile[]
  customSetup?: any
}

// Custom error overlay component
function ErrorOverlay() {
  const { sandpack } = useSandpack()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Listen for errors from the preview
    const listener = (message: any) => {
      if (message.type === 'error') {
        setError(message.data?.message || 'An error occurred')
      }
    }
    
    // This is a simplified error handling - in production you'd want more robust error tracking
    return () => {}
  }, [sandpack])

  return null
}

// Custom loading component
function LoadingOverlay() {
  return (
    <div className="absolute inset-0 flex items-center justify-center bg-[#0a0a0c]/90 backdrop-blur-sm z-10">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        className="flex flex-col items-center"
      >
        <Loader2 className="w-12 h-12 text-indigo-500 mb-4" />
        <span className="text-sm font-bold text-slate-400 tracking-widest uppercase">
          Preparing Preview
        </span>
      </motion.div>
    </div>
  )
}

export default function SandpackPreview({ files, customSetup }: SandpackPreviewProps) {
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [isReactApp, setIsReactApp] = useState(false)

  // Check if the generated files contain a React app
  useEffect(() => {
    const hasReactFiles = files.some(file => 
      file.path.includes('App.js') || 
      file.path.includes('App.jsx') ||
      file.path.includes('App.tsx') ||
      file.path.includes('index.js') ||
      file.path.includes('main.jsx') ||
      file.content.includes('react') ||
      file.content.includes('React')
    )
    setIsReactApp(hasReactFiles)
  }, [files])

  // Convert GeneratedFile[] to Sandpack files format
  const convertToSandpackFiles = () => {
    const sandpackFiles: Record<string, string> = {}
    
    files.forEach(file => {
      // Normalize the path for Sandpack
      let normalizedPath = file.path
      // Remove any prefix directories
      if (normalizedPath.includes('frontend/')) {
        normalizedPath = normalizedPath.replace('frontend/', '')
      }
      if (normalizedPath.includes('src/')) {
        normalizedPath = normalizedPath.replace('src/', '')
      }
      
      sandpackFiles[normalizedPath] = file.content
    })

    // Ensure we have at least an App.js file for Sandpack
    if (!sandpackFiles['App.js'] && !sandpackFiles['App.jsx'] && !sandpackFiles['App.tsx']) {
      // Try to find the main component file
      const mainComponent = files.find(f => 
        f.name.includes('App') || 
        f.name.includes('main') ||
        f.name.includes('index')
      )
      if (mainComponent) {
        sandpackFiles['App.js'] = mainComponent.content
      }
    }

    return sandpackFiles
  }

  const sandpackFiles = convertToSandpackFiles()

  // Default setup for React apps
  const defaultSetup = {
    dependencies: {
      'react': '18.2.0',
      'react-dom': '18.2.0',
      'react-scripts': '5.0.1'
    }
  }

  const handleLoadStart = () => {
    setIsLoading(true)
    setHasError(false)
  }

  const handleLoad = () => {
    setIsLoading(false)
    setHasError(false)
  }

  const handleError = (error: any) => {
    setIsLoading(false)
    setHasError(true)
    setErrorMessage(error?.message || 'Failed to load preview')
  }

  // If not a React app, show a message
  if (!isReactApp) {
    return (
      <div className="h-full w-full flex flex-col bg-[#0a0a0c]">
        <div className="h-12 flex items-center justify-between px-4 shrink-0 bg-[#0f1115]/80 border-b border-white/5">
          <div className="flex items-center gap-2">
            <Monitor className="w-4 h-4 text-indigo-400" />
            <h3 className="font-semibold text-xs text-slate-300 uppercase tracking-wider">Live Preview</h3>
          </div>
        </div>
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center max-w-md">
            <div className="w-20 h-20 bg-white/[0.02] border border-white/5 rounded-3xl flex items-center justify-center mb-6 mx-auto">
              <AlertCircle className="w-10 h-10 text-amber-500/50" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">React App Required</h3>
            <p className="text-sm text-slate-500 leading-relaxed">
              Live preview is only available for React applications. 
              Please generate a React-based project to see the live preview.
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full w-full flex flex-col bg-[#0a0a0c]">
      {/* Header */}
      <div className="h-12 flex items-center justify-between px-4 shrink-0 bg-[#0f1115]/80 border-b border-white/5">
        <div className="flex items-center gap-2">
          <Monitor className="w-4 h-4 text-emerald-400" />
          <h3 className="font-semibold text-xs text-slate-300 uppercase tracking-wider">Live Preview</h3>
          {isLoading && (
            <div className="flex items-center gap-2 ml-4">
              <Loader2 className="w-3 h-3 text-indigo-400 animate-spin" />
              <span className="text-[10px] text-slate-500 uppercase tracking-wider">Loading</span>
            </div>
          )}
          {!isLoading && !hasError && (
            <div className="flex items-center gap-2 ml-4">
              <CheckCircle className="w-3 h-3 text-emerald-400" />
              <span className="text-[10px] text-emerald-400 uppercase tracking-wider">Ready</span>
            </div>
          )}
        </div>
        <div className="flex items-center gap-2">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => {
              setIsLoading(true)
              setHasError(false)
              setTimeout(() => setIsLoading(false), 1000)
            }}
            className="p-2 text-slate-500 hover:text-indigo-400 rounded-lg transition-colors border border-transparent hover:border-indigo-500/20"
            title="Refresh Preview"
          >
            <RefreshCw className="w-4 h-4" />
          </motion.button>
        </div>
      </div>

      {/* Sandpack Container */}
      <div className="flex-1 relative overflow-hidden">
        <AnimatePresence mode="wait">
          {hasError ? (
            <motion.div
              key="error"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="absolute inset-0 flex items-center justify-center p-8 bg-[#0a0a0c]"
            >
              <div className="text-center max-w-md">
                <div className="w-20 h-20 bg-red-500/10 border border-red-500/20 rounded-3xl flex items-center justify-center mb-6 mx-auto">
                  <XCircle className="w-10 h-10 text-red-400" />
                </div>
                <h3 className="text-lg font-bold text-red-400 mb-2">Preview Error</h3>
                <p className="text-sm text-slate-500 mb-4">{errorMessage}</p>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => {
                    setHasError(false)
                    setIsLoading(true)
                    setTimeout(() => setIsLoading(false), 1000)
                  }}
                  className="px-6 py-2 bg-indigo-600 text-white rounded-lg text-sm font-semibold"
                >
                  Retry
                </motion.button>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="preview"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="h-full w-full"
            >
              <Sandpack
                template="react"
                files={sandpackFiles}
                theme="dark"
                customSetup={customSetup || defaultSetup}
                options={{
                  externalResources: [],
                }}
              >
                <SandpackLayout>
                  <div className="h-full w-full flex flex-col">
                    <div className="flex-1 relative">
                      {isLoading && <LoadingOverlay />}
                      <SandpackPreview 
                        style={{ 
                          height: '100%',
                          width: '100%',
                          border: 'none',
                          background: '#0a0a0c'
                        }}
                        onLoadStart={handleLoadStart}
                        onLoad={handleLoad}
                        onError={handleError}
                      />
                    </div>
                  </div>
                </SandpackLayout>
              </Sandpack>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
