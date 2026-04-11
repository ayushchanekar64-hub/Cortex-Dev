import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  File, 
  Folder, 
  FolderOpen,
  ChevronRight, 
  ChevronDown,
  FileCode,
  FileJson,
  FileText,
  Download
} from 'lucide-react'
import { GeneratedFile } from '../types'

interface DirectoryStructure {
  [key: string]: GeneratedFile | DirectoryStructure
}

interface FileStructureProps {
  files: GeneratedFile[]
  className?: string
}

export default function FileStructure({ files, className = '' }: FileStructureProps) {
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
    const extension = file.name.split('.').pop()?.toLowerCase()
    
    switch (extension) {
      case 'js':
      case 'jsx':
      case 'ts':
      case 'tsx':
        return <FileCode className="w-4 h-4 text-yellow-400" />
      case 'json':
        return <FileJson className="w-4 h-4 text-green-400" />
      case 'md':
        return <FileText className="w-4 h-4 text-blue-300" />
      default:
        return <File className="w-4 h-4 text-gray-400" />
    }
  }

  const buildDirectoryStructure = (files: GeneratedFile[]): GeneratedFile[] => {
    // Simple flat structure for now to avoid TypeScript issues
    return files.map(file => ({
      ...file,
      children: file.type === 'directory' ? [] : undefined
    }))
  }

  const renderFileStructure = (item: GeneratedFile, level: number = 0) => {
    if (item.type === 'directory') {
      const isExpanded = expandedFolders.has(item.id)
      const hasChildren = item.children && item.children.length > 0

      return (
        <div key={item.id}>
          <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: level * 0.05 }}
            className={`
              flex items-center gap-2 px-3 py-2 cursor-pointer
              hover:bg-gray-800 transition-all duration-200
              ${isExpanded ? 'bg-gray-800' : ''}
            `}
            style={{ paddingLeft: `${level * 16 + 8}px` }}
            onClick={() => {
              toggleFolder(item.id)
            }}
          >
            {isExpanded ? (
              <ChevronDown className="w-4 h-4 text-gray-400" />
            ) : (
              <ChevronRight className="w-4 h-4 text-gray-400" />
            )}
            <Folder className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-gray-300">{item.name}</span>
          </motion.div>
          {isExpanded && hasChildren && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="ml-2"
            >
              {item.children?.map(child => renderFileStructure(child, level + 1))}
            </motion.div>
          )}
        </div>
      )
    } else {
      return (
        <motion.div
          key={item.id}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: level * 0.05 }}
          className="flex items-center gap-2 px-3 py-2 hover:bg-gray-800 transition-all duration-200 cursor-pointer"
          style={{ paddingLeft: `${level * 16 + 24}px` }}
        >
          {getFileIcon(item)}
          <span className="text-sm text-gray-300">{item.name}</span>
        </motion.div>
      )
    }
  }

  const structure = buildDirectoryStructure(files)

  return (
    <div className={`space-y-1 ${className}`}>
      {structure.map(item => renderFileStructure(item))}
    </div>
  )
}
