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
    <div className="min-h-screen bg-white flex flex-col">
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
                  <span className="text-[1.2rem] md:text-[1.5rem] mb-1 font-semibold tracking-[-0.02em] text-[#111827]">
                    RAG Dataset Creator
                  </span>
                  <span className="text-[0.85rem] md:text-[0.9rem] text-[#6b7280] font-normal">
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

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-6 mt-auto">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <p className="text-sm text-gray-500">
            © {new Date().getFullYear()} RAG Dataset Creator
          </p>
        </div>
      </footer>
    </div>
  )
}

export default Layout 