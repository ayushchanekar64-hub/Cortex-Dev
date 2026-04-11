import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ChevronRight, 
  ChevronDown, 
  File, 
  Folder, 
  FolderOpen,
  FileCode,
  FileJson,
  FileText,
  Loader2
} from 'lucide-react'
import { GeneratedFile } from '../types'
import { Skeleton } from './LoadingStates'

interface FileExplorerProps {
  files: GeneratedFile[]
  selectedFile: GeneratedFile | null
  onSelectFile: (file: GeneratedFile) => void
}

export default function FileExplorer({ files, selectedFile, onSelectFile }: FileExplorerProps) {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set())

  const toggleFolder = (folderId: string) => {
    const newExpanded = new Set(expandedFolders)
    if (newExpanded.has(folderId)) {
      newExpanded.delete(folderId)
    } else {
      newExpanded.add(folderId)
    }
    setExpandedFolders(newExpanded)
  }

  const getFileIcon = (file: GeneratedFile) => {
    if (file.type === 'directory') {
      return expandedFolders.has(file.id) ? (
        <FolderOpen className="w-4 h-4 text-indigo-400" />
      ) : (
        <Folder className="w-4 h-4 text-indigo-400" />
      )
    }

    const extension = file.name.split('.').pop()?.toLowerCase()
    
    switch (extension) {
      case 'js':
      case 'jsx':
      case 'ts':
      case 'tsx':
        return <FileCode className="w-4 h-4 text-sky-400" />
      case 'json':
        return <FileJson className="w-4 h-4 text-emerald-400" />
      case 'css':
        return <FileCode className="w-4 h-4 text-pink-400" />
      case 'py':
        return <FileCode className="w-4 h-4 text-amber-400" />
      case 'md':
        return <FileText className="w-4 h-4 text-slate-400" />
      default:
        return <File className="w-4 h-4 text-slate-500" />
    }
  }

  const renderFile = (file: GeneratedFile, level: number = 0) => {
    const isExpanded = expandedFolders.has(file.id)
    const isSelected = selectedFile?.id === file.id

    return (
      <div key={file.id}>
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.2 }}
          className={`
            flex items-center gap-2.5 px-4 py-2 cursor-pointer
            group transition-all duration-300 relative
            ${isSelected 
              ? 'bg-indigo-500/10 text-white' 
              : 'text-slate-400 hover:bg-white/[0.03] hover:text-slate-200'}
          `}
          style={{ paddingLeft: `${level * 16 + 16}px` }}
          onClick={() => {
            if (file.type === 'directory') {
              toggleFolder(file.id)
            } else {
              onSelectFile(file)
            }
          }}
        >
          {isSelected && (
            <motion.div 
              layoutId="file-glow"
              className="absolute left-0 w-1 h-5 bg-indigo-500 rounded-r-full shadow-[0_0_10px_rgba(99,102,241,0.5)]"
            />
          )}

          {file.type === 'directory' && (
            <motion.div
              animate={{ rotate: isExpanded ? 90 : 0 }}
              transition={{ duration: 0.2 }}
            >
              <ChevronRight className={`w-3.5 h-3.5 transition-colors ${isSelected ? 'text-indigo-400' : 'text-slate-600 group-hover:text-slate-400'}`} />
            </motion.div>
          )}
          
          <div className={`${isSelected ? 'scale-110 opacity-100' : 'opacity-70 group-hover:opacity-100'} transition-all`}>
            {getFileIcon(file)}
          </div>
          
          <span className={`
            text-sm select-none tracking-tight transition-colors
            ${isSelected ? 'font-bold' : 'font-medium'}
          `}>
            {file.name}
          </span>
        </motion.div>

        {file.type === 'directory' && file.children && isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            {file.children.map(child => renderFile(child, level + 1))}
          </motion.div>
        )}
      </div>
    )
  }

  const organizeFiles = (files: GeneratedFile[]): GeneratedFile[] => {
    const rootFiles: GeneratedFile[] = []
    const dirMap = new Map<string, GeneratedFile>()

    files.forEach(file => {
      const parts = file.path.split('/')
      let currentPath = ''
      
      parts.forEach((part, i) => {
        const isLast = i === parts.length - 1
        const parentPath = currentPath
        currentPath = currentPath ? `${currentPath}/${part}` : part
        
        if (isLast) {
          const newFile = { ...file, id: currentPath }
          if (parentPath && dirMap.has(parentPath)) {
            dirMap.get(parentPath)!.children = dirMap.get(parentPath)!.children || []
            dirMap.get(parentPath)!.children!.push(newFile)
          } else {
            rootFiles.push(newFile)
          }
        } else {
          if (!dirMap.has(currentPath)) {
            const newDir: GeneratedFile = {
              id: currentPath,
              name: part,
              path: currentPath,
              type: 'directory',
              content: '',
              status: 'success',
              language: '',
              children: []
            }
            dirMap.set(currentPath, newDir)
            if (parentPath && dirMap.has(parentPath)) {
              dirMap.get(parentPath)!.children!.push(newDir)
            } else {
              rootFiles.push(newDir)
            }
          }
        }
      })
    })

    return rootFiles
  }

  const organizedFiles = organizeFiles(files)

  return (
    <div className="h-full flex flex-col bg-transparent">
      <div className="flex-1 overflow-y-auto custom-scrollbar py-2">
        {organizedFiles.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-600 px-8 text-center">
            <div className="bg-white/[0.02] p-6 rounded-3xl border border-white/5 mb-6">
              <File className="w-16 h-16 opacity-10" />
            </div>
            <p className="text-xs font-bold uppercase tracking-widest leading-loose">
              Vault Empty<br/>
              Awaiting Neural Synthesis
            </p>
          </div>
        ) : (
          <AnimatePresence mode="popLayout">
            {organizedFiles.map((file) => renderFile(file))}
          </AnimatePresence>
        )}
      </div>

      {files.length > 0 && (
        <div className="px-6 py-3 border-t border-white/5 bg-black/20 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-1 h-1 bg-indigo-500 rounded-full animate-pulse" />
            <span className="text-[10px] font-bold text-slate-500 tracking-widest uppercase">
              {files.length} Modules Synced
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
