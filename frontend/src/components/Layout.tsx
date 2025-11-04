import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { SparklesIcon } from '@heroicons/react/24/outline'

interface LayoutProps {
  children: ReactNode
}

function Layout({ children }: LayoutProps) {
  const location = useLocation()

  const isActive = (path: string) => location.pathname === path

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800/80 backdrop-blur-sm border-b border-gray-700/50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex justify-between items-center h-16">
            {/* Logo and Navigation */}
            <div className="flex items-center">
              <Link
                to="/"
                className="flex items-center space-x-3 text-white hover:text-blue-400 transition-colors group"
              >
                <SparklesIcon className="h-8 w-8 text-blue-500 group-hover:text-blue-400 transition-colors" />
                <span className="text-lg font-semibold tracking-tight">RAG Dataset Creator</span>
              </Link>

              <nav className="hidden md:flex items-center space-x-1 ml-8">
                <Link
                  to="/"
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive('/')
                      ? 'bg-blue-600/20 text-blue-400 shadow-lg shadow-blue-500/10'
                      : 'text-gray-300 hover:text-white hover:bg-gray-700/50'
                  }`}
                >
                  Home
                </Link>
              </nav>
            </div>

            {/* Right side - could add user menu or other actions here */}
            <div className="flex items-center space-x-4">
              <div className="text-xs text-gray-400 hidden sm:block">
                v1.0.0
              </div>
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