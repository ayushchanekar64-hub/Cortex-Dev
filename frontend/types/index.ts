export interface LogEntry {
  id: number
  timestamp: string
  message: string
  level: 'info' | 'success' | 'warning' | 'error'
}

export interface GeneratedFile {
  id: string
  name: string
  path: string
  content: string
  language: string
  type: 'file' | 'directory' | 'api' | 'component' | 'test' | 'doc'
  status?: 'pending' | 'success' | 'error'
  children?: GeneratedFile[]
}

export interface PipelineStatus {
  stage: 'planning' | 'generation' | 'debugging' | 'testing' | 'completed' | 'error'
  progress: number
  message: string
}

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
}
