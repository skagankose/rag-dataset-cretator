import { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getConfig } from '../lib/api'

interface LayoutProps {
  children: ReactNode
}

function Layout({ children }: LayoutProps) {
  // Fetch configuration to get prompt language
  const { data: config } = useQuery({
    queryKey: ['config'],
    queryFn: getConfig,
  })

  const promptLanguage = config?.prompt_language?.toLowerCase() || 'en'

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-gray-50 backdrop-blur-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex justify-between items-center py-3">
            {/* Logo and Navigation */}
            <div className="flex items-center">
              <Link
                to="/"
                className="flex items-center space-x-4 text-black hover:opacity-80 transition-opacity group"
              >
                <img 
                  src="/logo.png" 
                  alt="RAG Dataset Creator Logo" 
                  className="h-14 w-14 object-contain my-2"
                />
                <div className="flex flex-col">
                  <span className="text-xl font-bold tracking-tight leading-tight">
                    RAG Dataset Creator
                  </span>
                  <span className="text-xs text-gray-600 font-normal tracking-wide">
                    Transform articles into structured Q&A datasets
                  </span>
                </div>
              </Link>
            </div>

            {/* Right side - Version and Language badges */}
            <div className="flex items-center space-x-2">
              <span className="px-3 py-1 bg-gray-100 border border-gray-300 rounded-lg text-xs font-medium text-gray-700">
                v1.0.0
              </span>
              <span className="px-3 py-1 border rounded-lg text-xs font-medium bg-gray-900 border-gray-900 text-white">
                {promptLanguage.toUpperCase()}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main>
        {children}
      </main>
    </div>
  )
}

export default Layout 