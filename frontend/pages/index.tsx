import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Code2, 
  Terminal, 
  Loader2, 
  CheckCircle, 
  AlertCircle,
  MessageSquare,
  Search,
  Settings,
  Files,
  LayoutTemplate,
  User,
  Plus,
  FolderOpen,
  Save,
  History
} from 'lucide-react'
import PromptInput from '../components/PromptInput'
import FileExplorer from '../components/FileExplorer'
import CodePreview from '../components/CodePreview'
import LogsSection from '../components/LogsSection'
import ProjectOutput from '../components/ProjectOutput'
import LivePreview from '../components/LivePreview'
import { LogEntry, GeneratedFile } from '../types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8001'

export default function Home() {
  const [prompt, setPrompt] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedFiles, setGeneratedFiles] = useState<GeneratedFile[]>([])
  const [selectedFile, setSelectedFile] = useState<GeneratedFile | null>(null)
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [pipelineStatus, setPipelineStatus] = useState<'idle' | 'running' | 'completed' | 'error'>('idle')
  const logsEndRef = useRef<HTMLDivElement>(null)
  const [savedProjects, setSavedProjects] = useState<any[]>([])
  const [currentProjectName, setCurrentProjectName] = useState('')
  const [githubToken, setGithubToken] = useState('')
  const [showGithubModal, setShowGithubModal] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null)
  const [templates, setTemplates] = useState<any[]>([])
  const [showTemplateModal, setShowTemplateModal] = useState(false)

  // Layout State
  const [activeActivity, setActiveActivity] = useState<'files' | 'prompt' | 'history'>('prompt')
  const [activePanelTab, setActivePanelTab] = useState<'logs' | 'output'>('logs')
  const [activeEditorTab, setActiveEditorTab] = useState<'code' | 'preview'>('code')
  const [openMenu, setOpenMenu] = useState<string | null>(null)
  const [showSettings, setShowSettings] = useState(false)
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [user, setUser] = useState<{id: number, username: string} | null>(null)
  const [sidebarWidth, setSidebarWidth] = useState(320)
  const [isResizing, setIsResizing] = useState(false)
  const [isAppLoading, setIsAppLoading] = useState(true)
  const [panelHeight, setPanelHeight] = useState(288)
  const [isPanelResizing, setIsPanelResizing] = useState(false)

  // Splash Screen Effect
  useEffect(() => {
    // Check if user is in localStorage
    const savedUser = localStorage.getItem('auto_dev_user')
    if (savedUser) setUser(JSON.parse(savedUser))

    const timer = setTimeout(() => {
      setIsAppLoading(false)
    }, 2500)
    return () => clearTimeout(timer)
  }, [])

  const startResizing = (e: React.MouseEvent) => {
    setIsResizing(true)
  }

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return
      const newWidth = e.clientX - 64 // Subtract activity bar width
      if (newWidth > 200 && newWidth < 600) {
        setSidebarWidth(newWidth)
      }
    }

    const handleMouseUp = () => {
      setIsResizing(false)
    }

    if (isResizing) {
      window.addEventListener('mousemove', handleMouseMove)
      window.addEventListener('mouseup', handleMouseUp)
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isResizing])

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isPanelResizing) return
      const windowHeight = window.innerHeight
      const newHeight = windowHeight - e.clientY
      if (newHeight > 150 && newHeight < 600) {
        setPanelHeight(newHeight)
      }
    }

    const handleMouseUp = () => {
      setIsPanelResizing(false)
    }

    if (isPanelResizing) {
      window.addEventListener('mousemove', handleMouseMove)
      window.addEventListener('mouseup', handleMouseUp)
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isPanelResizing])

  // User Preferences
  const [settings, setSettings] = useState({
    fontSize: '14px',
    autoSave: true,
    aiModel: 'Gemini 1.5 Pro',
    debugMode: false,
    themeColor: '#6366f1',
    themeMode: 'neural-dark'
  })

  // Chat State
  const [messages, setMessages] = useState<{role: 'user' | 'assistant', content: string}[]>([
    { role: 'assistant', content: 'Hello! I am your Cortex-Dev. What would you like to build today?' }
  ])

  const themes = {
    'neural-dark': {
      bg: 'bg-[#0a0a0c]',
      sidebar: 'bg-[#12141a]/40',
      header: 'bg-[#0f1115]/80',
      accent: '#6366f1',
      text: 'text-slate-200'
    },
    'midnight-light': {
      bg: 'bg-[#f8fafc]',
      sidebar: 'bg-white/80',
      header: 'bg-white/90',
      accent: '#4f46e5',
      text: 'text-slate-900'
    },
    'cyberpunk': {
      bg: 'bg-[#050505]',
      sidebar: 'bg-[#1a0b2e]/60',
      header: 'bg-[#1a0b2e]/80',
      accent: '#ff00ff',
      text: 'text-cyan-400'
    }
  }

  const currentTheme = themes[settings.themeMode as keyof typeof themes] || themes['neural-dark']

  const menus = {
    'Project': ['New File', 'Save All', 'Download Code', 'Settings'],
    'View': ['Show Files', 'Show Chat', 'Terminal', 'Reset Layout'],
    'Deployment': ['Publish Page', 'Web Hosting', 'GitHub', 'Build App'],
    'Intelligence': ['Change AI Model', 'Auto Fix Bug', 'AI Logs', 'Settings'],
    'Help': ['How to use', 'Status', 'Support', 'About']
  }

  const addLog = (message: string, level: 'info' | 'success' | 'warning' | 'error' = 'info') => {
    const newLog: LogEntry = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      message,
      level
    }
    setLogs(prev => [...prev, newLog])
  }

  // Polling for live logs
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isGenerating) {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`${API_URL}/api/pipeline/progress`);
          if (res.ok) {
            const data = await res.json();
            if (data.status && data.status !== 'idle') {
              data.logs.forEach((msg: string) => {
                setLogs(prev => {
                  if (prev.some(l => l.message === msg)) return prev;
                  return [...prev, {
                    id: Date.now() + Math.random(),
                    timestamp: new Date().toISOString(),
                    message: msg,
                    level: 'info'
                  }];
                });
              });
            }
          }
        } catch (e) {
          console.error("Polling error", e);
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [isGenerating]);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs, messages, isGenerating])

  // Close menus when clicking outside
  useEffect(() => {
    const handleClick = () => setOpenMenu(null)
    window.addEventListener('click', handleClick)
    return () => window.removeEventListener('click', handleClick)
  }, [])

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      addLog('Please enter a prompt', 'warning')
      return
    }

    setIsGenerating(true)
    setPipelineStatus('running')
    setLogs([])
    setGeneratedFiles([])
    
    try {
      let files: GeneratedFile[] = []
      
      if (selectedTemplate) {
        // Use template as base
        addLog(`Loading template: ${selectedTemplate}...`, 'info')
        
        const templateRes = await fetch(`${API_URL}/api/templates/${selectedTemplate}`)
        const templateData = await templateRes.json()
        
        if (templateRes.ok && templateData) {
          addLog('Template loaded successfully', 'success')
          
          // Convert template files to GeneratedFile format
          const templateFiles = []
          let fileId = 1
          
          if (templateData.frontend_files) {
            Object.entries(templateData.frontend_files).forEach(([path, content]) => {
              templateFiles.push({
                id: String(fileId++),
                name: path.split('/').pop() || path,
                path: path,
                content: content,
                language: path.endsWith('.css') ? 'css' : 
                          path.endsWith('.json') ? 'json' : 
                          path.endsWith('.ts') || path.endsWith('.tsx') ? 'typescript' : 'text',
                type: 'component',
                status: 'success'
              })
            })
          }
          
          if (templateData.backend_files) {
            Object.entries(templateData.backend_files).forEach(([path, content]) => {
              templateFiles.push({
                id: String(fileId++),
                name: path.split('/').pop() || path,
                path: path,
                content: content,
                language: path.endsWith('.py') ? 'python' : 
                          path.endsWith('.json') ? 'json' : 'text',
                type: 'api',
                status: 'success'
              })
            })
          }
          
          files = templateFiles
          addLog(`Template contains ${files.length} files`, 'info')
          
          // Now ask AI to modify the template based on prompt
          addLog('Neural adaptation in progress...', 'info')
          
          const modifyRes = await fetch('${API_URL}/api/pipeline/modify', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              prompt: `Modify this ${templateData.name} template: ${prompt}`,
              current_files: files.map(f => ({ path: f.path, content: f.content })),
              model: settings.aiModel
            })
          })
          
          if (modifyRes.ok) {
            const modifyData = await modifyRes.json()
            if (modifyData.final_output && modifyData.final_output.generated_code) {
              // Merge modified files with template
              const modifiedFiles = modifyData.final_output.generated_code
              Object.entries(modifiedFiles).forEach(([path, content]) => {
                const existingIndex = files.findIndex(f => f.path === path)
                if (existingIndex >= 0) {
                  files[existingIndex].content = content
                } else {
                  files.push({
                    id: String(fileId++),
                    name: path.split('/').pop() || path,
                    path: path,
                    content: content,
                    language: path.endsWith('.css') ? 'css' : 
                              path.endsWith('.json') ? 'json' : 
                              path.endsWith('.py') ? 'python' : 'typescript',
                    type: path.includes('backend') ? 'api' : 'component',
                    status: 'success'
                  })
                }
              })
              addLog('Template adapted successfully', 'success')
            }
          }
        } else {
          throw new Error('Failed to load template')
        }
      } else {
        // Generate from scratch
        const response = await fetch('${API_URL}/api/pipeline/generate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            prompt,
            components: ['frontend', 'backend'],
            auto_fix: true,
            generate_tests: true,
            validate_api: false,
            model: settings.aiModel,
            debug: settings.debugMode
          })
        })

        if (!response.ok) {
          throw new Error(`Connection Error: ${response.status}`)
        }

        const result = await response.json()
        addLog('Neural surge detected. Materializing code...', 'info')
        
        let genCode = result.final_output?.generated_code || {};

        if (Object.keys(genCode).length > 0) {
          let fileId = 1
          Object.entries(genCode).forEach(([path, content]) => {
            if (typeof content === 'string') {
              const isBackend = path.toLowerCase().endsWith('.py') || path.toLowerCase().includes('requirement') || path.toLowerCase().includes('main.py');
              files.push({
                id: String(fileId++),
                name: path.split('/').pop() || path,
                path: path,
                content: content,
                language: path.endsWith('.css') ? 'css' : 
                          path.endsWith('.json') ? 'json' : 
                          path.endsWith('.py') ? 'python' : 'typescript',
                type: isBackend ? 'api' : 'component',
                status: 'success'
              })
            }
          })
        }
      }

      files.forEach((file, index) => {
        setTimeout(() => {
          setGeneratedFiles(prev => {
            const newFiles = [...prev, file];
            if (index === 0) setSelectedFile(file);
            return newFiles;
          })
          addLog(`Creating: ${file.path}`, 'success')

          const fileDescription = file.path.includes('frontend') ? 'Frontend component' :
                                  file.path.includes('backend') ? 'Backend API' :
                                  file.path.endsWith('.css') ? 'Stylesheet' :
                                  file.path.endsWith('.json') ? 'Configuration' :
                                  file.path.endsWith('.py') ? 'Python module' :
                                  'File'

          setMessages(prev => [...prev, { 
            role: 'assistant', 
            content: `📝 **Creating file**: \`${file.path}\`\n\n**Type**: ${fileDescription}\n**Status**: Generated successfully`
          }])
        }, index * 400)
      })

      setTimeout(() => {
        addLog('Optimization complete', 'success')
        
        setTimeout(async () => {
          addLog('Project ready to use!', 'success')
          setMessages(prev => [...prev, { 
            role: 'assistant', 
            content: '✨ **Success!** Your neural project has been fully materialized. You can now explore the code or switch to the **Live Preview** tab to see your creation in action!' 
          }])
          
          // Auto-save logic
          if (user) {
            try {
              addLog('Syncing project to neural cloud...', 'info')
              await fetch('${API_URL}/api/projects/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  name: `Project_${Date.now()}`, // Or get from prompt
                  prompt: prompt,
                  files: JSON.stringify(files),
                  user_id: user.id
                })
              })
              addLog('Project synced successfully!', 'success')
            } catch (e) {
              addLog('Cloud sync failed: Persistence offline', 'warning')
            }
          }

          setPipelineStatus('completed')
          setIsGenerating(false)
          setActiveActivity('files')
          setActivePanelTab('output')
          setActiveEditorTab('preview')
        }, 1500)
      }, files.length * 400 + 500)

    } catch (error) {
      console.error('Generation error:', error)
      addLog(`Error: ${error instanceof Error ? error.message : 'Something went wrong'}`, 'error')
      setMessages(prev => [...prev, { role: 'assistant', content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}` }])
      setPipelineStatus('error')
      setIsGenerating(false)
    }
  }

  const handleStop = () => {
    setIsGenerating(false)
    setPipelineStatus('idle')
    addLog('System interruption initiated by operator', 'warning')
  }

  const handleModifyChat = async (userMessage: string) => {
    if (generatedFiles.length === 0) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Please generate a project first before requesting modifications.' }])
      return
    }

    setIsGenerating(true)
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    addLog('Processing modification request...', 'info')

    try {
      const response = await fetch('${API_URL}/api/pipeline/modify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          files: generatedFiles.map(f => ({ path: f.path, name: f.name, content: f.content })),
          request: userMessage,
          model: 'gemini-2.0-flash'
        })
      })

      const data = await response.json()

      if (response.ok) {
        // Update files with modified content
        setGeneratedFiles(prev => prev.map(f => {
          const modified = data.modified_files.find(mf => mf.path === f.path)
          return modified ? { ...f, content: modified.content } : f
        }))

        // Update selected file if it was modified
        if (selectedFile) {
          const modified = data.modified_files.find(mf => mf.path === selectedFile.path)
          if (modified) {
            setSelectedFile({ ...selectedFile, content: modified.content })
          }
        }

        addLog('Code modified successfully', 'success')
        setMessages(prev => [...prev, { role: 'assistant', content: `✅ ${data.message}` }])
      } else {
        throw new Error(data.detail || 'Modification failed')
      }
    } catch (error) {
      console.error('Modification error:', error)
      addLog(`Error: ${error instanceof Error ? error.message : 'Modification failed'}`, 'error')
      setMessages(prev => [...prev, { role: 'assistant', content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}` }])
    } finally {
      setIsGenerating(false)
    }
  }

  const handleSaveProject = () => {
    if (generatedFiles.length === 0) return
    
    // Generate project name from first user message
    const firstUserMessage = messages.find(m => m.role === 'user')?.content || ''
    const projectName = currentProjectName || generateProjectName(firstUserMessage)
    
    const project = {
      id: Date.now(),
      name: projectName,
      files: generatedFiles,
      messages: messages,
      logs: logs,
      createdAt: new Date().toISOString(),
      userId: user?.id || null
    }
    
    setSavedProjects(prev => [...prev, project])
    
    // Save to localStorage with user-specific key
    const storageKey = user ? `savedProjects_${user.id}` : 'savedProjects'
    const existing = JSON.parse(localStorage.getItem(storageKey) || '[]')
    localStorage.setItem(storageKey, JSON.stringify([...existing, project]))
    
    addLog(`Project saved as "${projectName}"`, 'success')
  }

  const generateProjectName = (prompt: string): string => {
    if (!prompt) return `Project ${savedProjects.length + 1}`
    
    // Extract key words from prompt (first 3-4 meaningful words)
    const words = prompt
      .replace(/[^\w\s]/g, '') // Remove special characters
      .split(/\s+/)
      .filter(word => word.length > 2) // Filter short words
      .slice(0, 4) // Take first 4 meaningful words
    
    if (words.length === 0) return `Project ${savedProjects.length + 1}`
    
    // Capitalize each word and join
    const name = words
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ')
    
    // Limit to 30 characters
    return name.length > 30 ? name.substring(0, 30) + '...' : name
  }

  const handleLoadProject = (project: any) => {
    setGeneratedFiles(project.files)
    setMessages(project.messages)
    setLogs(project.logs)
    setCurrentProjectName(project.name)
    setSelectedFile(project.files[0] || null)
    setActiveActivity('files')
    addLog(`Loaded project "${project.name}"`, 'success')
  }

  const handleNewChat = () => {
    // Save current project if there are files
    if (generatedFiles.length > 0) {
      handleSaveProject()
    }
    
    // Reset state for new chat
    setGeneratedFiles([])
    setSelectedFile(null)
    setMessages([{ role: 'assistant', content: 'Hello! I am your Cortex-Dev. What would you like to build today?' }])
    setLogs([])
    setPrompt('')
    setCurrentProjectName('')
    setPipelineStatus('idle')
    setActiveActivity('prompt')
    addLog('Started new chat session', 'info')
  }

  // Load saved projects from localStorage on mount and when user changes
  useEffect(() => {
    const storageKey = user ? `savedProjects_${user.id}` : 'savedProjects'
    const saved = localStorage.getItem(storageKey)
    if (saved) {
      try {
        setSavedProjects(JSON.parse(saved))
      } catch (e) {
        console.error('Error loading saved projects:', e)
      }
    } else {
      setSavedProjects([])
    }
  }, [user])

  // Load GitHub token from localStorage
  useEffect(() => {
    const token = localStorage.getItem('github_token')
    if (token) {
      setGithubToken(token)
    }
  }, [])

  // Load templates from backend
  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        const res = await fetch('${API_URL}/api/templates/')
        const data = await res.json()
        if (res.ok) {
          setTemplates(data.templates || [])
        }
      } catch (error) {
        console.error('Failed to load templates:', error)
      }
    }
    fetchTemplates()
  }, [])

  // Menu item handlers
  const handleMenuAction = (menu: string, item: string) => {
    setOpenMenu(null)
    
    switch (menu) {
      case 'Project':
        switch (item) {
          case 'New File':
            addLog('New file created', 'info')
            break
          case 'Save All':
            handleSaveProject()
            break
          case 'Download Code':
            handleDownloadAll()
            break
          case 'Settings':
            setShowSettings(true)
            break
        }
        break
      case 'View':
        switch (item) {
          case 'Show Files':
            setActiveActivity('files')
            break
          case 'Show Chat':
            setActiveActivity('prompt')
            break
          case 'Terminal':
            setActivePanelTab('logs')
            break
          case 'Reset Layout':
            setSidebarWidth(320)
            addLog('Layout reset to default', 'info')
            break
        }
        break
      case 'Deployment':
        switch (item) {
          case 'Publish Page':
            addLog('Publish feature coming soon', 'info')
            break
          case 'Web Hosting':
            addLog('Web hosting feature coming soon', 'info')
            break
          case 'GitHub':
            addLog('GitHub integration coming soon', 'info')
            break
          case 'Build App':
            addLog('Build feature coming soon', 'info')
            break
        }
        break
      case 'Intelligence':
        switch (item) {
          case 'Change AI Model':
            setShowSettings(true)
            break
          case 'Auto Fix Bug':
            addLog('Auto-fix feature enabled', 'info')
            break
          case 'AI Logs':
            setActivePanelTab('logs')
            break
          case 'Settings':
            setShowSettings(true)
            break
        }
        break
      case 'Help':
        switch (item) {
          case 'How to use':
            setMessages(prev => [...prev, { 
              role: 'assistant', 
              content: '📖 **How to use:**\n1. Type your project idea in the chat\n2. Click Generate to create your project\n3. View and edit generated files\n4. Use chat to request modifications\n5. Save projects and start new chats' 
            }])
            break
          case 'Status':
            addLog('System status: All services operational', 'info')
            break
          case 'Support':
            addLog('Support: contact@autodevagent.com', 'info')
            break
          case 'About':
            setMessages(prev => [...prev, { 
              role: 'assistant', 
              content: '🤖 **About Cortex-Dev v3.0**\n\nAn AI-powered development agent that generates full-stack applications from natural language descriptions.' 
            }])
            break
        }
        break
    }
  }

  const handleDownloadAll = () => {
    if (generatedFiles.length === 0) return
    
    generatedFiles.forEach((file, index) => {
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
    addLog('Downloaded all files', 'success')
  }

  const handleExportToGitHub = async () => {
    if (!githubToken) {
      setShowGithubModal(true)
      return
    }
    
    if (generatedFiles.length === 0) {
      addLog('No files to export', 'warning')
      return
    }

    try {
      addLog('Connecting to GitHub...', 'info')
      
      // Get user info
      const userRes = await fetch('${API_URL}/api/github/user', {
        headers: { 'Authorization': `token ${githubToken}` }
      })
      
      if (!userRes.ok) {
        throw new Error('Invalid GitHub token')
      }
      
      const userData = await userRes.json()
      const owner = userData.username
      const repoName = currentProjectName.replace(/\s+/g, '-').toLowerCase()
      
      addLog(`Creating repository ${repoName}...`, 'info')
      
      // Create repository
      const createRes = await fetch('${API_URL}/api/github/create-repo', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `token ${githubToken}`
        },
        body: JSON.stringify({
          repo_name: repoName,
          description: `Auto-generated project: ${currentProjectName}`,
          private: false
        })
      })
      
      if (!createRes.ok) {
        const errorData = await createRes.json()
        throw new Error(errorData.detail || 'Failed to create repository')
      }
      
      const repoData = await createRes.json()
      addLog(`Repository created: ${repoData.repo_url}`, 'success')
      
      // Push files
      addLog('Pushing files to GitHub...', 'info')
      
      const filesData = generatedFiles.map(f => ({
        path: f.path,
        content: f.content
      }))
      
      const pushRes = await fetch('${API_URL}/api/github/push-files', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `token ${githubToken}`
        },
        body: JSON.stringify({
          owner: owner,
          repo: repoName,
          files: filesData,
          project_name: currentProjectName
        })
      })
      
      if (!pushRes.ok) {
        throw new Error('Failed to push files')
      }
      
      const pushData = await pushRes.json()
      addLog(`Successfully pushed ${pushData.success_count}/${pushData.total_files} files to GitHub`, 'success')
      addLog(`Repository URL: ${repoData.repo_url}`, 'success')
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `✅ **Successfully exported to GitHub!**\n\nRepository: ${repoData.repo_url}\nFiles pushed: ${pushData.success_count}/${pushData.total_files}`
      }])
      
    } catch (error: any) {
      addLog(`GitHub export failed: ${error.message}`, 'error')
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `❌ **GitHub export failed:** ${error.message}`
      }])
    }
  }

  return (
    <AnimatePresence mode="wait">
      {isAppLoading ? (
        <motion.div
          key="splash"
          initial={{ opacity: 1 }}
          exit={{ opacity: 0, scale: 1.1 }}
          transition={{ duration: 0.8, ease: "easeInOut" }}
          className="fixed inset-0 z-[999] bg-[#0a0a0c] flex flex-col items-center justify-center select-none"
        >
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: [0.8, 1.1, 1], opacity: 1 }}
            transition={{ duration: 1.5, ease: "easeOut" }}
            className="flex flex-col items-center"
          >
            <div className="w-24 h-24 mb-8 relative">
              <motion.div 
                animate={{ rotate: 360 }}
                transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                className="absolute inset-0 border-2 border-indigo-500/20 rounded-2xl"
              />
              <motion.div 
                animate={{ rotate: -360 }}
                transition={{ duration: 6, repeat: Infinity, ease: "linear" }}
                className="absolute inset-2 border-2 border-purple-500/20 rounded-xl"
              />
              <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl shadow-[0_0_50px_rgba(99,102,241,0.3)]">
                <Code2 className="w-12 h-12 text-white" />
              </div>
            </div>
            
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="text-center"
            >
              <h1 className="text-3xl font-black tracking-[0.3em] text-white text-shadow-glow uppercase">CORTEX-DEV</h1>
              <div className="mt-4 flex flex-col items-center space-y-3">
                <div className="w-48 h-1 bg-white/5 rounded-full overflow-hidden">
                  <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: "100%" }}
                    transition={{ duration: 2.5, ease: "easeInOut" }}
                    className="h-full bg-indigo-500 shadow-[0_0_10px_#6366f1]"
                  />
                </div>
                <span className="text-[10px] font-bold text-slate-500 tracking-[0.2em] uppercase">Neural Workspace Initializing...</span>
              </div>
            </motion.div>
          </motion.div>
        </motion.div>
      ) : (
        <motion.div 
          key="main"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className={`flex flex-col h-screen ${currentTheme.bg} ${settings.themeMode === 'midnight-light' ? 'text-slate-900' : 'text-[#e2e8f0]'} font-sans selection:bg-indigo-500/30 overflow-hidden cursor-default shadow-2xl`} 
          style={{ '--accent': currentTheme.accent } as any}
        >
      
      {/* Auth Modal */}
      <AnimatePresence>
        {showAuthModal && (
          <div className="fixed inset-0 z-[200] flex items-center justify-center p-6 backdrop-blur-xl bg-black/60">
            <motion.div 
              initial={{ opacity: 0, scale: 0.9, y: 30 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 30 }}
              className="bg-[#0f1115] border border-white/10 w-full max-w-md rounded-3xl shadow-[0_50px_100px_rgba(0,0,0,0.8)] overflow-hidden p-8"
            >
              <AuthForm 
                onSuccess={(userData) => {
                  setUser(userData)
                  localStorage.setItem('auto_dev_user', JSON.stringify(userData))
                  setShowAuthModal(false)
                }} 
                onClose={() => setShowAuthModal(false)}
              />
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* GitHub Token Modal */}
      <AnimatePresence>
        {showGithubModal && (
          <div className="fixed inset-0 z-[200] flex items-center justify-center p-6 backdrop-blur-xl bg-black/60">
            <motion.div 
              initial={{ opacity: 0, scale: 0.9, y: 30 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 30 }}
              className="bg-[#0f1115] border border-white/10 w-full max-w-md rounded-3xl shadow-[0_50px_100px_rgba(0,0,0,0.8)] overflow-hidden p-8"
            >
              <div className="space-y-6">
                <div className="text-center">
                  <h2 className="text-2xl font-black text-white uppercase tracking-widest leading-none">GitHub Setup</h2>
                  <p className="text-indigo-500 text-[10px] mt-3 uppercase tracking-[0.2em] font-black">Connect Your Repository</p>
                </div>

                <div className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-2">GitHub Personal Access Token</label>
                    <input 
                      type="password"
                      value={githubToken}
                      onChange={(e) => setGithubToken(e.target.value)}
                      className="w-full bg-black/40 border border-white/5 rounded-xl px-5 py-4 text-sm text-white focus:border-indigo-500/50 outline-none transition-all"
                      placeholder="ghp_xxxxxxxxxxxx"
                    />
                  </div>

                  <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-xl p-4">
                    <h3 className="text-xs font-bold text-indigo-400 uppercase tracking-widest mb-2">How to get your token:</h3>
                    <ol className="text-[11px] text-slate-400 space-y-1 list-decimal list-inside">
                      <li>Go to GitHub Settings → Developer settings</li>
                      <li>Click Personal access tokens → Tokens (classic)</li>
                      <li>Generate new token (classic)</li>
                      <li>Select scopes: repo, workflow</li>
                      <li>Copy the token and paste it above</li>
                    </ol>
                  </div>

                  <button 
                    onClick={() => {
                      if (githubToken) {
                        localStorage.setItem('github_token', githubToken)
                        setShowGithubModal(false)
                        handleExportToGitHub()
                      }
                    }}
                    className="w-full py-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-black text-xs uppercase tracking-[0.2em] transition-all shadow-lg shadow-indigo-500/20"
                  >
                    Connect & Export
                  </button>

                  <button 
                    onClick={() => setShowGithubModal(false)}
                    className="w-full text-[10px] font-bold text-slate-500 hover:text-slate-400 uppercase tracking-widest transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Template Selection Modal */}
      <AnimatePresence>
        {showTemplateModal && (
          <div className="fixed inset-0 z-[200] flex items-center justify-center p-6 backdrop-blur-xl bg-black/60">
            <motion.div 
              initial={{ opacity: 0, scale: 0.9, y: 30 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 30 }}
              className="bg-[#0f1115] border border-white/10 w-full max-w-4xl rounded-3xl shadow-[0_50px_100px_rgba(0,0,0,0.8)] overflow-hidden p-8"
            >
              <div className="space-y-6">
                <div className="text-center">
                  <h2 className="text-2xl font-black text-white uppercase tracking-widest leading-none">Select Template</h2>
                  <p className="text-indigo-500 text-[10px] mt-3 uppercase tracking-[0.2em] font-black">Choose a starting point for your project</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {templates.map((template) => (
                    <motion.button
                      key={template.id}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => {
                        setSelectedTemplate(template.id)
                        setShowTemplateModal(false)
                      }}
                      className={`p-6 rounded-2xl border-2 transition-all ${
                        selectedTemplate === template.id 
                          ? 'border-indigo-500 bg-indigo-500/10' 
                          : 'border-white/10 bg-white/5 hover:border-white/20'
                      }`}
                    >
                      <div className="text-4xl mb-4">{template.icon}</div>
                      <h3 className="text-lg font-bold text-white mb-2">{template.name}</h3>
                      <p className="text-xs text-slate-400 mb-4">{template.description}</p>
                      <div className="flex flex-wrap gap-2">
                        {template.features.slice(0, 3).map((feature, index) => (
                          <span key={index} className="text-[10px] px-2 py-1 bg-indigo-500/20 text-indigo-400 rounded-full">
                            {feature}
                          </span>
                        ))}
                      </div>
                    </motion.button>
                  ))}
                  
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => {
                      setSelectedTemplate(null)
                      setShowTemplateModal(false)
                    }}
                    className={`p-6 rounded-2xl border-2 transition-all ${
                      selectedTemplate === null 
                        ? 'border-emerald-500 bg-emerald-500/10' 
                        : 'border-white/10 bg-white/5 hover:border-white/20'
                    }`}
                  >
                    <div className="text-4xl mb-4">✨</div>
                    <h3 className="text-lg font-bold text-white mb-2">Start from Scratch</h3>
                    <p className="text-xs text-slate-400 mb-4">Generate completely custom code from your prompt</p>
                    <div className="flex flex-wrap gap-2">
                      <span className="text-[10px] px-2 py-1 bg-emerald-500/20 text-emerald-400 rounded-full">
                        Custom
                      </span>
                    </div>
                  </motion.button>
                </div>

                <div className="flex justify-center space-x-4">
                  <button 
                    onClick={() => setShowTemplateModal(false)}
                    className="px-8 py-3 bg-white/5 border border-white/10 text-white rounded-xl font-black text-xs uppercase tracking-[0.2em] transition-all"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Settings Modal */}
      <AnimatePresence>
        {showSettings && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-12 backdrop-blur-md bg-black/40">
            <motion.div 
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className={`${settings.themeMode === 'midnight-light' ? 'bg-white' : 'bg-[#0f1115]'} border border-white/10 w-full max-w-4xl h-full max-h-[700px] rounded-3xl shadow-[0_50px_100px_rgba(0,0,0,0.6)] flex overflow-hidden`}
            >
              {/* Settings Sidebar */}
              <div className={`w-1/4 ${settings.themeMode === 'midnight-light' ? 'bg-slate-100' : 'bg-black/20'} border-r border-white/5 p-8 space-y-8`}>
                <h2 className={`text-xl font-bold tracking-tight ${settings.themeMode === 'midnight-light' ? 'text-slate-900' : 'text-white'} mb-10`}>Settings</h2>
                <div className="space-y-4">
                  {['Editor', 'AI Model', 'Appearance', 'About'].map(cat => (
                    <button key={cat} className={`w-full text-left px-4 py-2 text-sm font-semibold ${settings.themeMode === 'midnight-light' ? 'text-slate-600' : 'text-slate-400'} hover:text-indigo-500 transition-colors`}>
                      {cat}
                    </button>
                  ))}
                </div>
                <div className="flex-1" />
                <button 
                  onClick={() => setShowSettings(false)}
                  className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold text-sm transition-all"
                >
                  Close
                </button>
              </div>

              {/* Settings Content */}
              <div className="flex-1 p-12 overflow-y-auto custom-scrollbar">
                <div className="max-w-xl space-y-12">
                  <section>
                    <h3 className={`text-lg font-bold ${settings.themeMode === 'midnight-light' ? 'text-slate-900' : 'text-white'} mb-6 flex items-center gap-3`}>
                      <LayoutTemplate className="w-5 h-5 text-indigo-400" />
                      Visual Appearance
                    </h3>
                    <div className="grid grid-cols-2 gap-4">
                      {[
                        { id: 'neural-dark', name: 'Neural Dark', bg: 'bg-[#0a0a0c]' },
                        { id: 'midnight-light', name: 'Midnight Light', bg: 'bg-[#f8fafc]' },
                        { id: 'cyberpunk', name: 'Cyberpunk', bg: 'bg-[#050505]' }
                      ].map(t => (
                        <button 
                          key={t.id}
                          onClick={() => setSettings({...settings, themeMode: t.id})}
                          className={`p-4 rounded-2xl border-2 transition-all flex flex-col items-center gap-3 ${settings.themeMode === t.id ? 'border-indigo-500 bg-indigo-500/10' : 'border-white/5 hover:border-white/20'}`}
                        >
                          <div className={`w-full h-12 rounded-lg ${t.bg} border border-white/10`} />
                          <span className={`text-xs font-bold ${settings.themeMode === 'midnight-light' ? 'text-slate-900' : 'text-slate-300'}`}>{t.name}</span>
                        </button>
                      ))}
                    </div>
                  </section>

                  <section>
                    <h3 className={`text-lg font-bold ${settings.themeMode === 'midnight-light' ? 'text-slate-900' : 'text-white'} mb-6 flex items-center gap-3`}>
                      <Code2 className="w-5 h-5 text-indigo-400" />
                      Editor Settings
                    </h3>
                    <div className="space-y-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className={`text-sm font-bold ${settings.themeMode === 'midnight-light' ? 'text-slate-700' : 'text-slate-200'}`}>Font Size</p>
                        </div>
                        <select 
                          value={settings.fontSize}
                          onChange={(e) => setSettings({...settings, fontSize: e.target.value})}
                          className="bg-black/10 border border-white/10 rounded-lg px-4 py-2 text-xs outline-none"
                        >
                          <option value="12px">Small (12px)</option>
                          <option value="14px">Normal (14px)</option>
                          <option value="16px">Large (16px)</option>
                        </select>
                      </div>
                    </div>
                  </section>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* 1. Futuristic Header */}
      <div className={`h-16 flex items-center justify-between px-8 ${currentTheme.header} backdrop-blur-md border-b border-white/5 select-none relative z-50 transition-colors`}>
        <motion.div 
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="flex items-center space-x-5 cursor-pointer"
        >
          <div className="w-11 h-11 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-[0_0_20px_rgba(99,102,241,0.4)]">
            <Code2 className="w-7 h-7 text-white" />
          </div>
          <div className="flex flex-col">
            <span className="text-base font-black tracking-wider text-white leading-none text-shadow-glow uppercase">CORTEX-DEV</span>
            <span className="text-[10px] text-indigo-400/80 font-mono tracking-[0.2em] uppercase mt-1.5">Version 3.0</span>
          </div>
        </motion.div>
        
        <div className="flex items-center space-x-6 text-sm font-medium text-slate-400">
          <div className="flex items-center space-x-4">
            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowTemplateModal(true)}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-purple-500/10 border border-purple-500/20 hover:bg-purple-500/20 transition-all"
              title="Select Template"
            >
              <FolderOpen className="w-4 h-4 text-purple-400" />
              <span className="text-xs font-bold text-purple-400">TEMPLATES</span>
            </motion.button>

            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleNewChat}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20 hover:bg-indigo-500/20 transition-all"
              title="New Chat"
            >
              <Plus className="w-4 h-4 text-indigo-400" />
              <span className="text-xs font-bold text-indigo-400">NEW CHAT</span>
            </motion.button>

            {generatedFiles.length > 0 && (
              <motion.button 
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleSaveProject}
                className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 hover:bg-emerald-500/20 transition-all"
                title="Save Project"
              >
                <Save className="w-4 h-4 text-emerald-400" />
                <span className="text-xs font-bold text-emerald-400">SAVE</span>
              </motion.button>
            )}

            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleExportToGitHub}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gray-700/10 border border-gray-500/20 hover:bg-gray-700/20 transition-all"
              title="Export to GitHub"
            >
              <FolderOpen className="w-4 h-4 text-gray-400" />
              <span className="text-xs font-bold text-gray-400">GITHUB</span>
            </motion.button>

            {savedProjects.length > 0 && (
              <div className="relative">
                <motion.button 
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setOpenMenu(openMenu === 'projects' ? null : 'projects')}
                  className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-purple-500/10 border border-purple-500/20 hover:bg-purple-500/20 transition-all"
                  title="Load Project"
                >
                  <FolderOpen className="w-4 h-4 text-purple-400" />
                  <span className="text-xs font-bold text-purple-400">LOAD</span>
                </motion.button>

                {openMenu === 'projects' && (
                  <div className="absolute right-0 mt-2 w-64 bg-[#1a1a1a] border border-white/10 rounded-xl shadow-2xl z-50 max-h-96 overflow-y-auto">
                    <div className="p-3 border-b border-white/10">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Saved Projects</span>
                    </div>
                    {savedProjects.map(project => (
                      <button
                        key={project.id}
                        onClick={() => {
                          handleLoadProject(project)
                          setOpenMenu(null)
                        }}
                        className="w-full text-left px-4 py-3 hover:bg-white/5 transition-colors border-b border-white/5 last:border-0"
                      >
                        <div className="text-sm text-white font-medium">{project.name}</div>
                        <div className="text-[10px] text-slate-500 mt-1">
                          {new Date(project.createdAt).toLocaleDateString()} • {project.files.length} files
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="w-px h-8 bg-white/10"></div>

          <div className="flex items-center space-x-8">
            {Object.keys(menus).map(menu => (
              <div key={menu} className="relative active-menu-container">
                <motion.button 
                  whileHover={{ scale: 1.1, textShadow: '0 0 10px rgba(99,102,241,0.5)', color: '#818cf8' }}
                  whileTap={{ scale: 0.9 }}
                  onClick={(e) => {
                    e.stopPropagation()
                    setOpenMenu(openMenu === menu ? null : menu)
                  }}
                  className={`transition-colors cursor-pointer outline-none bg-transparent border-none font-semibold ${openMenu === menu ? 'text-indigo-400' : ''}`}
                >
                  {menu}
                </motion.button>

                <AnimatePresence>
                  {openMenu === menu && (
                    <motion.div
                      initial={{ opacity: 0, y: 10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 10, scale: 0.95 }}
                      className="absolute top-full left-0 mt-3 w-56 bg-[#161920]/90 backdrop-blur-xl border border-white/10 rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] overflow-hidden"
                    >
                      <div className="p-2 space-y-1">
                        {menus[menu as keyof typeof menus].map((item, i) => (
                          <motion.button 
                            key={item}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.05 }}
                            whileHover={{ backgroundColor: 'rgba(99, 102, 241, 0.1)', color: '#fff', x: 5 }}
                            onClick={() => handleMenuAction(menu, item)}
                            className="w-full text-left px-4 py-2.5 rounded-xl text-[13px] font-medium text-slate-400 transition-all flex items-center justify-between group cursor-pointer outline-none border-none bg-transparent"
                          >
                            <span>{item}</span>
                            <div className="w-1 h-1 bg-indigo-500/0 group-hover:bg-indigo-500 rounded-full transition-all" />
                          </motion.button>
                        ))}
                      </div>
                      <div className="bg-white/5 px-4 py-2 text-[10px] uppercase font-bold text-slate-500 tracking-widest border-t border-white/5">
                        Neural Verified
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))}
          </div>
          <div className="h-5 w-[1px] bg-white/10" />
          <div className="flex items-center space-x-6 shrink-0">
            {user ? (
              <div className="flex items-center space-x-4">
                <div className="flex flex-col items-end">
                  <span className="text-[11px] font-black text-indigo-400 uppercase tracking-[0.1em] leading-none">{user.username}</span>
                </div>
                <div className="relative">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setOpenMenu(openMenu === 'profile' ? null : 'profile')}
                    className="w-9 h-9 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center cursor-pointer outline-none border-none bg-transparent"
                  >
                    <User className="w-5 h-5 text-indigo-400" />
                  </motion.button>

                  {openMenu === 'profile' && (
                    <motion.div
                      initial={{ opacity: 0, y: 10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      className="absolute right-0 mt-2 w-48 bg-[#161920]/90 backdrop-blur-xl border border-white/10 rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] overflow-hidden z-50"
                    >
                      <div className="p-2 space-y-1">
                        <motion.button
                          whileHover={{ backgroundColor: 'rgba(99, 102, 241, 0.1)' }}
                          onClick={() => {
                            setShowSettings(true)
                            setOpenMenu(null)
                          }}
                          className="w-full text-left px-4 py-2.5 rounded-xl text-[13px] font-medium text-slate-400 transition-all cursor-pointer outline-none border-none bg-transparent"
                        >
                          Settings
                        </motion.button>
                        <motion.button
                          whileHover={{ backgroundColor: 'rgba(239, 68, 68, 0.1)' }}
                          onClick={() => {
                            localStorage.removeItem('auto_dev_user')
                            setUser(null)
                            setOpenMenu(null)
                          }}
                          className="w-full text-left px-4 py-2.5 rounded-xl text-[13px] font-medium text-red-400 transition-all cursor-pointer outline-none border-none bg-transparent"
                        >
                          Sign Out
                        </motion.button>
                      </div>
                    </motion.div>
                  )}
                </div>
              </div>
            ) : (
              <motion.button 
                whileHover={{ scale: 1.05, boxShadow: '0 0 20px rgba(99,102,241,0.2)' }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowAuthModal(true)}
                className="px-6 py-2 bg-indigo-600 text-white rounded-xl text-[11px] font-black uppercase tracking-[0.2em] shadow-lg shadow-indigo-500/20 transition-all cursor-pointer outline-none border-none"
              >
                Sign In
              </motion.button>
            )}

            <motion.button 
              whileHover={{ rotate: 90, scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => setShowSettings(true)}
              className="p-2.5 text-slate-500 hover:text-slate-300 transition-colors cursor-pointer outline-none border-none bg-transparent"
            >
              <Settings className="w-6 h-6" />
            </motion.button>
          </div>
        </div>
      </div>

      {/* Main Layout Area */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* 2. Glass Activity Bar */}
        <div className="w-14 bg-[#0f1115]/60 border-r border-white/5 flex flex-col items-center py-6 space-y-6 shrink-0 backdrop-blur-sm">
          {[
            { id: 'prompt', icon: MessageSquare, title: 'Chat' },
            { id: 'files', icon: Files, title: 'My Files' },
            { id: 'history', icon: History, title: 'History' },
            { id: 'search', icon: Search, title: 'Search' }
          ].map(item => (
            <motion.button 
              key={item.id}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => setActiveActivity(item.id as any)}
              className={`p-2.5 rounded-xl transition-all relative group outline-none ${
                activeActivity === item.id 
                ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 shadow-[0_0_20px_rgba(99,102,241,0.1)]' 
                : 'text-slate-500 hover:text-slate-300 hover:bg-white/5'
              }`}
              title={item.title}
            >
              <item.icon className="w-6 h-6" />
              {activeActivity === item.id && (
                <motion.div 
                   layoutId="active-indicator"
                  className="absolute left-[-16px] w-1 h-6 bg-indigo-500 rounded-r-full shadow-[0_0_8px_indigo]"
                />
              )}
            </motion.button>
          ))}
          
          <div className="flex-1" />
          
          <motion.button 
            whileHover={{ scale: 1.1, rotate: 45 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => setShowSettings(true)}
            className="p-2.5 text-slate-500 hover:text-slate-300 transition-colors outline-none border-none bg-transparent"
          >
            <Settings className="w-6 h-6" />
          </motion.button>
        </div>

        {/* 3. Neural Sidebar */}
        <div 
          style={{ width: `${sidebarWidth}px` }}
          className={`${currentTheme.sidebar} backdrop-blur-lg border-r border-white/5 flex flex-col shrink-0 overflow-hidden transition-colors relative`}
        >
          <motion.div 
            whileHover={{ backgroundColor: 'rgba(255,255,255,0.02)' }}
            className="h-14 px-6 flex items-center justify-between border-b border-white/5 shrink-0 cursor-pointer"
          >
            <span className="text-sm font-bold uppercase tracking-widest text-slate-300">
              {activeActivity === 'files' ? 'My Project Files' : 'Talk to AI'}
            </span>
            <div className="flex space-x-2">
              <div className="w-2.5 h-2.5 rounded-full bg-indigo-500/30" />
              <div className="w-2.5 h-2.5 rounded-full bg-indigo-500/60" />
            </div>
          </motion.div>
          
          <div className="flex-1 overflow-hidden flex flex-col">
            {activeActivity === 'prompt' ? (
              <div className="flex-1 flex flex-col overflow-hidden">
                <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar bg-black/5">
                  {messages.map((msg, i) => (
                    <motion.div
                      initial={{ opacity: 0, y: 10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      key={i}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-[85%] p-5 rounded-2xl text-[17px] leading-relaxed shadow-xl ${
                        msg.role === 'user' 
                          ? 'bg-indigo-600 text-white rounded-tr-none' 
                          : `${settings.themeMode === 'midnight-light' ? 'bg-slate-200 text-slate-800' : 'bg-white/5 text-slate-200'} border border-white/5 rounded-tl-none`
                      }`}>
                        {msg.content}
                      </div>
                    </motion.div>
                  ))}
                  {isGenerating && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="flex justify-start"
                    >
                      <div className="p-4 rounded-2xl bg-white/5 border border-white/5 rounded-tl-none flex items-center space-x-2">
                        <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" />
                        <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                        <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.4s]" />
                      </div>
                    </motion.div>
                  )}
                  <div ref={logsEndRef} />
                </div>

                <div className="p-4 border-t border-white/5 bg-black/20">
                  <PromptInput 
                    value={prompt}
                    onChange={setPrompt}
                    onGenerate={(v) => {
                      const userMsg = v || prompt;
                      if (!userMsg) return;
                      setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
                      setPrompt('');
                      
                      // If files are already generated, use modification chat
                      if (generatedFiles.length > 0) {
                        handleModifyChat(userMsg);
                      } else {
                        handleGenerate();
                      }
                    }} 
                    isGenerating={isGenerating} 
                    onStop={handleStop}
                    placeholder={generatedFiles.length > 0 ? "Ask me to modify the code or add features..." : "Ask me something..."}
                  />
                </div>
              </div>
            ) : activeActivity === 'history' ? (
              <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
                <div className="mb-4">
                  <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-2">Saved Projects</h3>
                  <p className="text-xs text-slate-500">Click on any project to restore it completely</p>
                </div>
                {savedProjects.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-64 opacity-50">
                    <History className="w-12 h-12 mb-4 text-slate-500" />
                    <p className="text-sm text-slate-500">No saved projects yet</p>
                    <p className="text-xs text-slate-600 mt-2">Generate a project and save it to see it here</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {savedProjects.map(project => (
                      <motion.button
                        key={project.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        whileHover={{ scale: 1.02, backgroundColor: 'rgba(99, 102, 241, 0.1)' }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => handleLoadProject(project)}
                        className="w-full p-4 bg-white/5 border border-white/10 rounded-xl text-left hover:border-indigo-500/30 transition-all"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className="text-sm font-semibold text-white mb-1">{project.name}</h4>
                            <p className="text-xs text-slate-500 mb-2">
                              {new Date(project.createdAt).toLocaleDateString()} at {new Date(project.createdAt).toLocaleTimeString()}
                            </p>
                            <div className="flex items-center space-x-4 text-xs text-slate-400">
                              <span className="flex items-center space-x-1">
                                <Files className="w-3 h-3" />
                                <span>{project.files.length} files</span>
                              </span>
                              <span className="flex items-center space-x-1">
                                <MessageSquare className="w-3 h-3" />
                                <span>{project.messages.length} messages</span>
                              </span>
                            </div>
                          </div>
                          <FolderOpen className="w-5 h-5 text-indigo-400 shrink-0 ml-2" />
                        </div>
                      </motion.button>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="flex-1 overflow-y-auto p-2 custom-scrollbar">
                <FileExplorer
                  files={generatedFiles}
                  selectedFile={selectedFile}
                  onSelectFile={setSelectedFile}
                />
              </div>
            )}
          </div>

          {/* Resize Handle */}
          <div
            onMouseDown={startResizing}
            className={`absolute right-0 top-0 bottom-0 w-1 cursor-col-resize hover:bg-indigo-500/50 transition-colors z-50 ${isResizing ? 'bg-indigo-500/50' : ''}`}
          />
        </div>

        {/* Workspace Center */}
        <div className="flex-1 flex flex-col overflow-hidden bg-gradient-to-br from-[#0a0a0c] to-[#12141a]">
          
          {/* 4. Glass Editor Tab Bar */}
          <div className="flex-1 flex flex-col min-h-0">
            <div className="h-12 flex items-center bg-[#0f1115]/80 border-b border-white/5 shrink-0 px-2 space-x-1 overflow-x-auto no-scrollbar">
              {[
                { id: 'code', icon: Code2, label: selectedFile ? selectedFile.name : 'Console', color: 'text-indigo-400' },
                { id: 'preview', icon: LayoutTemplate, label: 'Live Preview', color: 'text-emerald-400' }
              ].map(tab => (
                <motion.button 
                  key={tab.id}
                  whileHover={{ scale: 1.02, backgroundColor: 'rgba(255,255,255,0.05)' }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setActiveEditorTab(tab.id as any)}
                  className={`flex items-center px-6 h-9 rounded-lg space-x-3 text-[13px] font-bold transition-all outline-none whitespace-nowrap ${
                    activeEditorTab === tab.id 
                    ? 'bg-indigo-500/10 text-white border border-indigo-500/20 shadow-[0_0_15px_rgba(99,102,241,0.1)]' 
                    : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <tab.icon className={`w-5 h-5 ${activeEditorTab === tab.id ? tab.color : 'text-slate-500'}`} />
                  <span>{tab.label}</span>
                </motion.button>
              ))}
            </div>
            
            {/* Main Stage */}
            <div className="flex-1 overflow-hidden relative">
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeEditorTab}
                  initial={{ opacity: 0, scale: 0.99 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.2 }}
                  className="h-full"
                >
                  {activeEditorTab === 'code' ? (
                    selectedFile ? (
                      <CodePreview file={selectedFile} files={generatedFiles} fontSize={settings.fontSize} />
                    ) : (
                      <motion.div 
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex items-center justify-center h-full flex-col space-y-6 cursor-pointer group"
                        onClick={() => setActiveActivity('prompt')}
                      >
                        <div className="relative">
                          <motion.div 
                            animate={{ scale: [1, 1.2, 1], opacity: [0.1, 0.2, 0.1] }}
                            transition={{ duration: 4, repeat: Infinity }}
                            className="absolute inset-0 bg-indigo-500 blur-3xl"
                          />
                          <Code2 className="w-24 h-24 text-indigo-500/20 relative z-10 group-hover:text-indigo-500/40 transition-colors" />
                        </div>
                        <p className="text-slate-500 font-bold tracking-[0.2em] uppercase text-[10px] group-hover:text-slate-300 transition-colors">Awaiting neural input. Click to start.</p>
                      </motion.div>
                    )
                  ) : (
                    <LivePreview 
                      files={generatedFiles} 
                      onFileUpdate={(file, newContent) => {
                        setGeneratedFiles(prev => prev.map(f => 
                          f.path === file.path ? { ...f, content: newContent } : f
                        ))
                        if (selectedFile?.path === file.path) {
                          setSelectedFile({ ...selectedFile, content: newContent })
                        }
                      }}
                    />
                  )}
                </motion.div>
              </AnimatePresence>
            </div>
          </div>

          {/* 5. Cyber Panel (Bottom) */}
          <div 
            className="flex flex-col bg-[#0a0a0f]/95 border-t border-white/10 shrink-0 backdrop-blur-2xl shadow-2xl"
            style={{ height: `${panelHeight}px` }}
          >
            {/* Resize Handle */}
            <div 
              className="h-1 bg-transparent hover:bg-indigo-500/30 cursor-row-resize transition-colors flex items-center justify-center group"
              onMouseDown={() => setIsPanelResizing(true)}
            >
              <div className="w-12 h-1 bg-white/20 rounded-full group-hover:bg-indigo-400 transition-colors" />
            </div>

            {/* Panel Header */}
            <div className="flex px-6 items-center space-x-8 shrink-0 h-12 border-b border-white/10 bg-gradient-to-r from-white/[0.02] to-transparent">
              {[
                { id: 'logs', label: 'SYSTEM LOGS', icon: Terminal },
                { id: 'output', label: 'ALL FILES', icon: Files }
              ].map(tab => (
                <motion.button 
                  key={tab.id}
                  whileHover={{ y: -2 }}
                  whileTap={{ y: 0 }}
                  onClick={() => setActivePanelTab(tab.id as any)}
                  className={`text-[11px] font-bold tracking-[0.15em] h-full flex items-center space-x-2 relative transition-all outline-none ${
                    activePanelTab === tab.id ? 'text-indigo-400' : 'text-slate-500 hover:text-slate-300'
                  }`}
                >
                  <tab.icon className="w-3.5 h-3.5" />
                  <span>{tab.label}</span>
                  {activePanelTab === tab.id && (
                    <motion.div 
                      layoutId="panel-accent"
                      className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-indigo-500 to-purple-500 shadow-[0_0_15px_rgba(99,102,241,0.5)]"
                    />
                  )}
                </motion.button>
              ))}
              
              <div className="flex-1" />
              
              <div className="text-[10px] text-slate-600 font-mono">
                {panelHeight}px
              </div>
            </div>
            
            {/* Panel Content */}
            <div className="flex-1 overflow-hidden bg-black/40">
              {activePanelTab === 'logs' ? (
                <div className="h-full custom-scrollbar cursor-text">
                  <LogsSection logs={logs} />
                </div>
              ) : (
                <ProjectOutput files={generatedFiles} className="h-full" />
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 6. Neural Status Bar */}
      <div className="h-8 bg-[#0f1115] border-t border-white/5 text-slate-400 flex items-center justify-between px-6 text-[11px] font-bold tracking-wider shrink-0 uppercase select-none">
        <div className="flex items-center space-x-8">
          <div className="flex items-center space-x-4 text-indigo-400">
            <motion.button 
              whileHover={{ scale: 1.05, backgroundColor: 'rgba(52,211,153,0.1)' }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center space-x-2 px-3 py-1 rounded bg-indigo-500/10 border border-indigo-500/20 cursor-pointer outline-none"
            >
              <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
              <span>NO ERRORS</span>
            </motion.button>
            <motion.button 
              whileHover={{ scale: 1.05, backgroundColor: 'rgba(251,191,36,0.1)' }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center space-x-2 px-3 py-1 rounded bg-amber-500/10 border border-amber-400/20 cursor-pointer outline-none"
            >
              <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
              <span>NO WARNINGS</span>
            </motion.button>
          </div>
          
          <motion.div 
            whileHover={{ letterSpacing: '0.15em' }}
            className="flex items-center space-x-3 text-slate-500 cursor-help"
          >
            <div className={`w-2 h-2 rounded-full ${pipelineStatus === 'running' ? 'bg-indigo-400 animate-ping shadow-[0_0_10px_indigo]' : 'bg-slate-600'}`} />
            <span>SYSTEM: {pipelineStatus === 'idle' ? 'STANDBY' : pipelineStatus.toUpperCase()}</span>
          </motion.div>
        </div>
        
        <div className="flex items-center space-x-8">
          <motion.span whileHover={{ color: '#fff' }} className="text-slate-500 cursor-pointer uppercase">UTF-8</motion.span>
          <motion.span whileHover={{ color: '#fff' }} className="text-slate-500 cursor-pointer uppercase">TYPESCRIPT</motion.span>
          <motion.div 
            whileHover={{ backgroundColor: '#4f46e5' }}
            className="bg-indigo-600 px-4 h-full flex items-center text-white space-x-2 cursor-pointer transition-colors"
          >
            <Terminal className="w-3.5 h-3.5" />
            <span className="tracking-[0.1em]">CONNECTED</span>
          </motion.div>
        </div>
      </div>

      {/* Global CSS for scrollbars and effects */}
      <style jsx global>{`
        ${isResizing ? `* { cursor: col-resize !important; user-select: none !important; }` : ''}
        .custom-scrollbar::-webkit-scrollbar { width: 6px; height: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(99, 102, 241, 0.1); border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(99, 102, 241, 0.2); }
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .text-shadow-glow { text-shadow: 0 0 10px rgba(255,255,255,0.3); }
      `}</style>
    </motion.div>
      )}
    </AnimatePresence>
  )
}

function AuthForm({ onSuccess, onClose }: { onSuccess: (user: any) => void, onClose: () => void }) {
  const [isLogin, setIsLogin] = useState(true)
  const [formData, setFormData] = useState({ username: '', email: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showForgotPassword, setShowForgotPassword] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const body = isLogin 
        ? { username_or_email: formData.username || formData.email, password: formData.password }
        : { username: formData.username, email: formData.email, password: formData.password }

      const res = await fetch(`${API_URL}/api/auth/${isLogin ? 'login' : 'register'}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })

      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Auth failed')

      onSuccess(data.user)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-black text-white uppercase tracking-widest leading-none">{isLogin ? 'Welcome Back' : 'Create Account'}</h2>
        <p className="text-indigo-500 text-[10px] mt-3 uppercase tracking-[0.2em] font-black">Cortex-Dev</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {!isLogin && (
          <div className="space-y-2">
             <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-2 group-focus-within:text-indigo-400">Username</label>
             <input 
               type="text" 
               required
               value={formData.username}
               onChange={(e) => setFormData({...formData, username: e.target.value})}
               className="w-full bg-black/40 border border-white/5 rounded-xl px-5 py-4 text-sm text-white focus:border-indigo-500/50 outline-none transition-all"
               placeholder="Username"
             />
          </div>
        )}
        <div className="space-y-2">
           <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-2">{isLogin ? 'Username or Email' : 'Email Address'}</label>
           <input 
             type={isLogin ? "text" : "email"} 
             required
             value={isLogin ? formData.username : formData.email}
             onChange={(e) => isLogin ? setFormData({...formData, username: e.target.value}) : setFormData({...formData, email: e.target.value})}
             className="w-full bg-black/40 border border-white/5 rounded-xl px-5 py-4 text-sm text-white focus:border-indigo-500/50 outline-none transition-all"
             placeholder={isLogin ? "Username or Email" : "email@example.com"}
           />
        </div>
        <div className="space-y-2">
           <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-2">Password</label>
           <input 
             type="password" 
             required
             value={formData.password}
             onChange={(e) => setFormData({...formData, password: e.target.value})}
             className="w-full bg-black/40 border border-white/5 rounded-xl px-5 py-4 text-sm text-white focus:border-indigo-500/50 outline-none transition-all"
             placeholder="••••••••"
           />
        </div>

        {error && (
          <motion.p 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-red-400 text-[10px] font-bold uppercase tracking-widest text-center bg-red-400/5 py-2 rounded-lg border border-red-400/10"
          >
            {error}
          </motion.p>
        )}

        <button 
          type="submit" 
          disabled={loading}
          className="w-full py-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-black text-xs uppercase tracking-[0.2em] transition-all shadow-lg shadow-indigo-500/20 disabled:opacity-50 mt-4"
        >
          {loading ? 'Processing...' : isLogin ? 'Login' : 'Sign Up'}
        </button>
      </form>

      {isLogin && (
        <div className="text-center">
          <button 
            onClick={() => setShowForgotPassword(true)}
            className="text-[10px] font-bold text-indigo-400 hover:text-indigo-300 transition-colors uppercase tracking-widest"
          >
            Forgot Password?
          </button>
        </div>
      )}

      <div className="text-center pt-6 border-t border-white/5">
        <button 
          onClick={() => {
            setIsLogin(!isLogin)
            setShowForgotPassword(false)
          }}
          className="text-xs font-bold text-slate-500 hover:text-indigo-400 transition-colors uppercase tracking-widest"
        >
          {isLogin ? "New to Auto Dev? Create Account" : "Already have an account? Login"}
        </button>
      </div>

      {showForgotPassword && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 pt-4 border-t border-white/5"
        >
          <p className="text-xs text-slate-400 text-center mb-4">Enter your email to reset your password</p>
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-2">Email Address</label>
              <input 
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                className="w-full bg-black/40 border border-white/5 rounded-xl px-5 py-4 text-sm text-white focus:border-indigo-500/50 outline-none transition-all"
                placeholder="email@example.com"
              />
            </div>
            <button 
              onClick={async () => {
                setLoading(true)
                setError('')
                try {
                  const res = await fetch('${API_URL}/api/auth/forgot-password', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: formData.email })
                  })
                  const data = await res.json()
                  if (res.ok) {
                    setError('')
                    alert('Password reset link sent to your email! Check your inbox.')
                    setShowForgotPassword(false)
                  } else {
                    setError(data.detail || 'Failed to send reset link')
                  }
                } catch (err: any) {
                  setError('Failed to send reset link')
                } finally {
                  setLoading(false)
                }
              }}
              disabled={loading}
              className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-black text-[11px] uppercase tracking-[0.2em] transition-all disabled:opacity-50"
            >
              {loading ? 'Sending...' : 'Send Reset Link'}
            </button>
            <button 
              onClick={() => setShowForgotPassword(false)}
              className="w-full text-[10px] font-bold text-slate-500 hover:text-slate-400 uppercase tracking-widest transition-colors"
            >
              Cancel
            </button>
          </div>
        </motion.div>
      )}
      
      <button 
        onClick={onClose}
        className="w-full text-[10px] font-bold text-slate-700 hover:text-slate-500 uppercase tracking-[0.3em] transition-colors mt-2"
      >
        Close
      </button>
    </div>
  )
}
