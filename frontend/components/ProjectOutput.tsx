import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Download, 
  FileText, 
  FolderOpen,
  Share2,
  Eye,
  EyeOff,
  Copy,
  Trash2,
  Package,
  Code2,
  FileJson,
  FileCode
} from 'lucide-react'
import { GeneratedFile } from '../types'

interface ProjectOutputProps {
  files: GeneratedFile[]
  className?: string
}

export default function ProjectOutput({ files, className = '' }: ProjectOutputProps) {
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set())
  const [viewMode, setViewMode] = useState<'structure' | 'preview' | 'both'>('both')
  const [isDownloading, setIsDownloading] = useState(false)
  const [copiedFile, setCopiedFile] = useState<string | null>(null)

  const getFileStats = () => {
    const stats = {
      total: files.length,
      byType: {} as Record<string, number>,
      byLanguage: {} as Record<string, number>
    }

    files.forEach(file => {
      stats.byType[file.type] = (stats.byType[file.type] || 0) + 1
      stats.byLanguage[file.language] = (stats.byLanguage[file.language] || 0) + 1
    })

    return stats
  }

  const handleFileSelect = (fileId: string) => {
    setSelectedFiles(prev => {
      const newSet = new Set(prev)
      if (newSet.has(fileId)) {
        newSet.delete(fileId)
      } else {
        newSet.add(fileId)
      }
      return newSet
    })
  }

  const handleSelectAll = () => {
    setSelectedFiles(new Set(files.map(f => f.id)))
  }

  const handleDownloadFile = async (file: GeneratedFile) => {
    try {
      const blob = new Blob([file.content], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = file.name
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Download failed:', error)
    }
  }

  const handleDownloadSelected = async () => {
    const selectedFileObjects = files.filter(f => selectedFiles.has(f.id))
    
    if (selectedFileObjects.length === 0) {
      return
    }

    setIsDownloading(true)
    
    try {
      // Create ZIP file
      const JSZip = await import('jszip')
      const zip = new JSZip.default()
      
      selectedFileObjects.forEach(file => {
        zip.file(file.path, file.content)
      })
      
      const content = await zip.generateAsync({ type: 'blob' })
      const url = URL.createObjectURL(content)
      
      const a = document.createElement('a')
      a.href = url
      a.download = 'project-files.zip'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
    } catch (error) {
      console.error('ZIP download failed:', error)
    } finally {
      setIsDownloading(false)
    }
  }

  const handleCopyAll = async () => {
    const selectedFileObjects = files.filter(f => selectedFiles.has(f.id))
    
    if (selectedFileObjects.length === 0) {
      return
    }

    try {
      const allContent = selectedFileObjects.map(f => 
        `// ${f.path}\n${'='.repeat(50)}\n${f.content}\n${'='.repeat(50)}`
      ).join('\n\n')
      
      await navigator.clipboard.writeText(allContent)
      setCopiedFile('all selected files')
      setTimeout(() => setCopiedFile(null), 2000)
    } catch (error) {
      console.error('Copy failed:', error)
    }
  }

  const stats = getFileStats()

  return (
    <div className={`h-full flex flex-col bg-gray-900 ${className}`}>
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-800">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-300 flex items-center gap-2">
            <Package className="w-4 h-4" />
            Project Output
          </h2>
          
          <div className="flex items-center gap-2">
            <div className="text-xs text-gray-500">
              {files.length} files • {Object.keys(stats.byType).length} types
            </div>
            
            <div className="flex items-center gap-1">
              <button
                onClick={() => setViewMode('structure')}
                className={`px-2 py-1 text-xs rounded transition-colors ${
                  viewMode === 'structure' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                <FolderOpen className="w-3 h-3" />
                Structure
              </button>
              
              <button
                onClick={() => setViewMode('preview')}
                className={`px-2 py-1 text-xs rounded transition-colors ${
                  viewMode === 'preview' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                <Eye className="w-3 h-3" />
                Preview
              </button>
              
              <button
                onClick={() => setViewMode('both')}
                className={`px-2 py-1 text-xs rounded transition-colors ${
                  viewMode === 'both' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                <FileText className="w-3 h-3" />
                Both
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* File Structure Panel */}
        {(viewMode === 'structure' || viewMode === 'both') && (
          <div className="w-80 border-r border-gray-800 flex flex-col">
            <div className="px-4 py-3 border-b border-gray-800">
              <h3 className="text-sm font-medium text-gray-300 mb-3">File Structure</h3>
              
              {/* Selection Controls */}
              <div className="flex items-center justify-between mb-3">
                <button
                  onClick={handleSelectAll}
                  className="text-xs text-blue-500 hover:text-blue-400 transition-colors"
                >
                  Select All
                </button>
                
                <div className="text-xs text-gray-500">
                  {selectedFiles.size} selected
                </div>
              </div>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4">
              {files.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-32 text-gray-500">
                  <FileText className="w-8 h-8 mb-2 opacity-50" />
                  <p className="text-sm">No files generated</p>
                </div>
              ) : (
                <div className="space-y-1">
                  {files.map(file => (
                    <motion.div
                      key={file.id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: files.indexOf(file) * 0.05 }}
                      className={`
                        flex items-center gap-2 p-2 rounded cursor-pointer
                        hover:bg-gray-800 transition-all duration-200
                        ${selectedFiles.has(file.id) ? 'bg-blue-600/20' : ''}
                      `}
                      onClick={() => handleFileSelect(file.id)}
                    >
                      <input
                        type="checkbox"
                        checked={selectedFiles.has(file.id)}
                        onChange={() => handleFileSelect(file.id)}
                        className="rounded border-gray-600 bg-gray-800 text-blue-500"
                      />
                      
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          {file.type === 'directory' ? (
                            <FolderOpen className="w-4 h-4 text-blue-400" />
                          ) : (
                            <>
                              {file.language === 'typescript' && <FileCode className="w-4 h-4 text-blue-400" />}
                              {file.language === 'json' && <FileJson className="w-4 h-4 text-green-400" />}
                              {file.language === 'javascript' && <FileCode className="w-4 h-4 text-yellow-400" />}
                              {!file.language && <FileText className="w-4 h-4 text-gray-400" />}
                            </>
                          )}
                          
                          <div className="flex-1 min-w-0">
                            <div className="text-sm text-gray-300 truncate">{file.name}</div>
                            <div className="text-xs text-gray-500 truncate">{file.path}</div>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => handleDownloadFile(file)}
                            className="p-1 hover:bg-gray-700 rounded transition-colors"
                            title="Download file"
                          >
                            <Download className="w-3 h-3 text-gray-400" />
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
            
            {/* Structure Footer */}
            {files.length > 0 && (
              <div className="px-4 py-3 border-t border-gray-800">
                <div className="flex items-center justify-between">
                  <div className="text-xs text-gray-500">
                    {selectedFiles.size} of {files.length} selected
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <button
                      onClick={handleCopyAll}
                      disabled={selectedFiles.size === 0}
                      className="px-2 py-1 text-xs bg-gray-800 text-gray-400 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Copy className="w-3 h-3" />
                      Copy Selected
                    </button>
                    
                    <button
                      onClick={handleDownloadSelected}
                      disabled={selectedFiles.size === 0 || isDownloading}
                      className="px-2 py-1 text-xs bg-blue-600 text-white rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
                    >
                      {isDownloading ? (
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        >
                          <Download className="w-3 h-3" />
                        </motion.div>
                      ) : (
                        <>
                          <Download className="w-3 h-3" />
                          Download ZIP
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Code Preview Panel */}
        {(viewMode === 'preview' || viewMode === 'both') && (
          <div className="flex-1 overflow-hidden">
            <div className="h-full flex flex-col">
              <div className="px-4 py-3 border-b border-gray-800">
                <h3 className="text-sm font-medium text-gray-300">Code Preview</h3>
              </div>
              
              <div className="flex-1 overflow-auto">
                {files.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-gray-500">
                    <Code2 className="w-12 h-12 mb-3 opacity-50" />
                    <p className="text-sm">No files to preview</p>
                    <p className="text-xs mt-1">Generate a project to see code</p>
                  </div>
                ) : (
                  <div className="h-full">
                    {viewMode === 'preview' ? (
                      /* Single file preview */
                      <div className="h-full">
                        {files.length > 0 && (
                          <div className="h-full">
                            <div className="px-4 py-2 bg-gray-800 border-b border-gray-700">
                              <div className="flex items-center justify-between">
                                <span className="text-sm text-gray-300">{files[0].name}</span>
                                <div className="flex items-center gap-2">
                                  <span className="text-xs text-gray-500">{files[0].path}</span>
                                  <button
                                    onClick={() => handleDownloadFile(files[0])}
                                    className="p-1 hover:bg-gray-700 rounded transition-colors"
                                    title="Download file"
                                  >
                                    <Download className="w-3 h-3 text-gray-400" />
                                  </button>
                                </div>
                              </div>
                            </div>
                            <div className="flex-1 overflow-auto">
                              <pre className="p-4 text-sm text-gray-100 font-mono leading-relaxed">
                                <code>{files[0].content}</code>
                              </pre>
                            </div>
                          </div>
                        )}
                      </div>
                    ) : (
                      /* Split view with file list and preview */
                      <div className="flex h-full">
                        <div className="w-64 border-r border-gray-800 overflow-y-auto">
                          <div className="p-2">
                            {files.map(file => (
                              <button
                                key={file.id}
                                onClick={() => {
                                  // In a real implementation, this would switch the previewed file
                                }}
                                className={`
                                  w-full text-left p-2 rounded hover:bg-gray-800 transition-colors
                                  text-xs text-gray-400 truncate
                                  ${selectedFiles.has(file.id) ? 'bg-blue-600/20' : ''}
                                `}
                              >
                                <div className="flex items-center gap-2">
                                  {file.language === 'typescript' && <FileCode className="w-3 h-3 text-blue-400" />}
                                  {file.language === 'json' && <FileJson className="w-3 h-3 text-green-400" />}
                                  {file.language === 'javascript' && <FileCode className="w-3 h-3 text-yellow-400" />}
                                  {!file.language && <FileText className="w-3 h-3 text-gray-400" />}
                                  <span className="truncate">{file.name}</span>
                                </div>
                              </button>
                            ))}
                          </div>
                        </div>
                        
                        <div className="flex-1 overflow-auto">
                          <div className="px-4 py-2 bg-gray-800 border-b border-gray-700">
                            <span className="text-sm text-gray-300">
                              {files.length > 0 ? files[0].name : 'Select a file'}
                            </span>
                          </div>
                          <div className="flex-1 overflow-auto">
                            <pre className="p-4 text-sm text-gray-100 font-mono leading-relaxed">
                              <code>{files.length > 0 ? files[0].content : 'Select a file to preview'}</code>
                            </pre>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Stats Footer */}
      <div className="px-4 py-3 border-t border-gray-800">
        <div className="flex items-center justify-between">
          <div className="text-xs text-gray-500">
            Total: {stats.total} files
          </div>
          
          <div className="flex items-center gap-4">
            {Object.entries(stats.byType).map(([type, count]) => (
              <div key={type} className="flex items-center gap-1">
                <div className={`w-2 h-2 rounded-full ${
                  type === 'file' ? 'bg-blue-500' : 'bg-green-500'
                }`} />
                <span className="text-xs text-gray-400">
                  {count} {type}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Copy Notification */}
      <AnimatePresence>
        {copiedFile && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="fixed bottom-4 right-4 bg-green-600 text-white px-3 py-2 rounded-lg shadow-lg text-sm z-50"
          >
            <div className="flex items-center gap-2">
              <Copy className="w-4 h-4" />
              <span>Copied {copiedFile === 'all selected files' ? 'all selected files' : 'file'}!</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
