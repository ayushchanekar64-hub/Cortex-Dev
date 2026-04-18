import { useState } from 'react'
import { Monitor, Download, AlertTriangle, Save, Edit3, Eye } from 'lucide-react'
import CodePreview from './CodePreview'

interface LivePreviewProps {
  files: any[]
  onFileUpdate?: (file: any, newContent: string) => void
}

export default function LivePreview({ files, onFileUpdate }: LivePreviewProps) {
  const [selectedFile, setSelectedFile] = useState<any>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [editedContent, setEditedContent] = useState('')

  // Filter frontend files
  const frontendFiles = files.filter((file: any) => {
    const path = file.path || file.name
    return !path.includes('-backend/') && !path.startsWith('backend/') && !path.endsWith('.py')
  })

  if (!files || files.length === 0) {
    return (
      <div className="flex items-center justify-center h-full w-full bg-[#1e1e1e]">
        <div className="flex flex-col items-center opacity-50">
          <Monitor className="w-16 h-16 mb-4 text-[#858585]" />
          <p className="text-[#858585]">Generate an application to see the files</p>
        </div>
      </div>
    )
  }

  // Auto-select first file
  if (!selectedFile && frontendFiles.length > 0) {
    setSelectedFile(frontendFiles[0])
  }

  const handleDownloadAll = () => {
    frontendFiles.forEach((file: any, index: number) => {
      setTimeout(() => {
        const blob = new Blob([file.content], { type: 'text/plain' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = file.name || 'file.txt'
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      }, index * 100)
    })
  }

  const handleEditClick = () => {
    setIsEditing(true)
    setEditedContent(selectedFile?.content || '')
  }

  const handleSaveClick = () => {
    if (selectedFile && onFileUpdate) {
      onFileUpdate(selectedFile, editedContent)
      setIsEditing(false)
    }
  }

  const handleCancelClick = () => {
    setIsEditing(false)
    setEditedContent('')
  }

  // Check if it's a React app
  const isReactApp = frontendFiles.some((file: any) => {
    const content = file.content || ''
    const path = file.path || file.name || ''
    return (
      path.includes('App.js') ||
      path.includes('App.jsx') ||
      path.includes('App.tsx') ||
      path.includes('index.js') ||
      content.includes('react') ||
      content.includes('React')
    )
  })

  return (
    <div className="h-full w-full flex flex-col bg-[#0a0a0c] overflow-hidden">
      {/* Header */}
      <div className="h-12 flex items-center justify-between px-4 shrink-0 bg-[#0f1115]/80 border-b border-white/5">
        <div className="flex items-center gap-2">
          <Monitor className="w-4 h-4 text-emerald-400" />
          <h3 className="font-semibold text-xs text-slate-300 uppercase tracking-wider">
            {isReactApp ? 'Code View' : 'Generated Files'}
          </h3>
        </div>
        <div className="flex items-center gap-2">
          {selectedFile && !isEditing && onFileUpdate && (
            <button
              onClick={handleEditClick}
              className="p-1.5 hover:bg-white/10 rounded transition-colors"
              title="Edit file"
            >
              <Edit3 className="w-3.5 h-3.5 text-slate-400 hover:text-white" />
            </button>
          )}
          {isEditing && (
            <>
              <button
                onClick={handleSaveClick}
                className="p-1.5 hover:bg-white/10 rounded transition-colors"
                title="Save changes"
              >
                <Save className="w-3.5 h-3.5 text-green-500 hover:text-green-400" />
              </button>
              <button
                onClick={handleCancelClick}
                className="p-1.5 hover:bg-white/10 rounded transition-colors"
                title="Cancel"
              >
                <Eye className="w-3.5 h-3.5 text-slate-400 hover:text-white" />
              </button>
            </>
          )}
          <button
            onClick={handleDownloadAll}
            className="p-1.5 hover:bg-white/10 rounded transition-colors"
            title="Download all files"
          >
            <Download className="w-3.5 h-3.5 text-slate-400 hover:text-white" />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-hidden">
        <div className="h-full flex">
          {/* File List */}
          <div className="w-48 border-r border-white/5 overflow-y-auto custom-scrollbar bg-black/20">
            <div className="p-2">
              {frontendFiles.map((file: any, index: number) => {
                const fileName = file.name || file.path?.split('/').pop() || 'Unknown'
                const isSelected = selectedFile?.path === file.path
                return (
                  <button
                    key={index}
                    onClick={() => {
                      setSelectedFile(file)
                      setIsEditing(false)
                      setEditedContent('')
                    }}
                    className={`w-full text-left px-3 py-2 text-xs rounded mb-1 transition-colors ${
                      isSelected
                        ? 'bg-indigo-500/20 text-indigo-400'
                        : 'text-slate-500 hover:bg-white/5 hover:text-slate-300'
                    }`}
                  >
                    {fileName}
                  </button>
                )
              })}
            </div>
          </div>

          {/* File Content */}
          <div className="flex-1 overflow-hidden flex flex-col">
            {selectedFile ? (
              isEditing ? (
                <div className="h-full flex flex-col">
                  <div className="h-8 flex items-center justify-between px-4 bg-[#0f1115] border-b border-white/5">
                    <span className="text-xs text-slate-500">
                      Editing: {selectedFile.path || selectedFile.name}
                    </span>
                  </div>
                  <textarea
                    value={editedContent}
                    onChange={(e) => setEditedContent(e.target.value)}
                    className="flex-1 bg-[#0a0a0c] text-slate-300 p-4 font-mono text-xs resize-none focus:outline-none custom-scrollbar"
                    spellCheck={false}
                  />
                </div>
              ) : (
                <CodePreview file={selectedFile} files={frontendFiles} fontSize="12px" />
              )
            ) : (
              <div className="h-full flex items-center justify-center">
                <p className="text-xs text-slate-500">Select a file to view</p>
              </div>
            )}

            {/* Info message */}
            {isReactApp && (
              <div className="px-4 py-2 bg-[#0f1115] border-t border-white/5">
                <div className="flex items-center gap-2 text-[10px] text-slate-500">
                  <AlertTriangle className="w-3 h-3 text-indigo-400" />
                  <span>React app detected. Code view enabled.</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
