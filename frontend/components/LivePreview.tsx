import { useState } from 'react'
import { Monitor, FileCode, Download, AlertTriangle, Save, Edit3, Eye } from 'lucide-react'
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
    const path = file.path || file.name;
    return !path.includes('-backend/') && 
           !path.startsWith('backend/') && 
           !path.endsWith('.py');
  });

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

  return (
    <div className="h-full w-full flex flex-col bg-[#1e1e1e] overflow-hidden">
      <div className="h-10 flex items-center justify-between px-4 shrink-0 bg-[#2d2d2d] border-b border-[#2d2d2d]">
        <div className="flex items-center gap-2">
          <FileCode className="w-4 h-4 text-[#4ec9b0]" />
          <h3 className="font-semibold text-xs text-[#cccccc] uppercase tracking-wider">Generated Files</h3>
        </div>
        <div className="flex items-center gap-2">
          {selectedFile && !isEditing && onFileUpdate && (
            <button 
              onClick={handleEditClick}
              className="p-1.5 hover:bg-white/10 rounded transition-colors"
              title="Edit file"
            >
              <Edit3 className="w-3.5 h-3.5 text-[#858585] hover:text-white" />
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
                <Eye className="w-3.5 h-3.5 text-[#858585] hover:text-white" />
              </button>
            </>
          )}
          <button 
            onClick={handleDownloadAll}
            className="p-1.5 hover:bg-white/10 rounded transition-colors"
            title="Download all files"
          >
            <Download className="w-3.5 h-3.5 text-[#858585] hover:text-white" />
          </button>
        </div>
      </div>
      
      <div className="flex-1 overflow-hidden flex">
        {/* File List */}
        <div className="w-48 border-r border-[#2d2d2d] overflow-y-auto custom-scrollbar">
          <div className="p-2">
            {frontendFiles.map((file: any, index: number) => {
              const fileName = file.name || file.path?.split('/').pop() || 'Unknown';
              const isSelected = selectedFile?.path === file.path;
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
                      ? 'bg-[#4ec9b0]/20 text-[#4ec9b0]' 
                      : 'text-[#858585] hover:bg-white/5 hover:text-white'
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
                <div className="h-8 flex items-center justify-between px-4 bg-[#1a1a1a] border-b border-[#2d2d2d]">
                  <span className="text-xs text-[#858585]">Editing: {selectedFile.path || selectedFile.name}</span>
                </div>
                <textarea
                  value={editedContent}
                  onChange={(e) => setEditedContent(e.target.value)}
                  className="flex-1 bg-[#0f1115] text-[#cccccc] p-4 font-mono text-xs resize-none focus:outline-none custom-scrollbar"
                  spellCheck={false}
                />
              </div>
            ) : (
              <CodePreview file={selectedFile} files={frontendFiles} fontSize="12px" />
            )
          ) : (
            <div className="h-full flex items-center justify-center">
              <p className="text-xs text-[#858585]">Select a file to view</p>
            </div>
          )}
          
          {/* Info message */}
          <div className="px-4 py-2 bg-[#1a1a1a] border-t border-[#2d2d2d]">
            <div className="flex items-center gap-2 text-[10px] text-[#858585]">
              <AlertTriangle className="w-3 h-3 text-yellow-500" />
              <span>Browser-based rendering not available. Download files and run locally with npm install && npm start</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
