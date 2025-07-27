import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { 
  DocumentTextIcon,
  DocumentArrowDownIcon,
  MagnifyingGlassIcon,
  ChevronLeftIcon,
} from '@heroicons/react/24/outline'

import { getArticle, getChunks, getFileUrl, downloadFile } from '../lib/api'

function ArticlePage() {
  const { articleId } = useParams<{ articleId: string }>()
  const [searchQuery, setSearchQuery] = useState('')

  const { data: article, isLoading: articleLoading } = useQuery({
    queryKey: ['article', articleId],
    queryFn: () => getArticle(articleId!),
    enabled: !!articleId,
  })

  const { data: chunks = [], isLoading: chunksLoading } = useQuery({
    queryKey: ['chunks', articleId],
    queryFn: () => getChunks(articleId!),
    enabled: !!articleId,
  })

  const filteredChunks = chunks.filter(chunk =>
    chunk.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
    chunk.section.toLowerCase().includes(searchQuery.toLowerCase()) ||
    chunk.heading_path.toLowerCase().includes(searchQuery.toLowerCase()) ||
    chunk.id.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const downloadChunksAsJson = () => {
    const chunksData = {
      article: {
        id: article?.id,
        title: article?.title,
        url: article?.url,
        lang: article?.lang,
        created_at: article?.created_at,
        stats: article?.stats,
        options: article?.options
      },
      chunks: chunks,
      metadata: {
        total_chunks: chunks.length,
        export_date: new Date().toISOString()
      }
    }
    
    const dataStr = JSON.stringify(chunksData, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    
    const link = document.createElement('a')
    link.href = url
    link.download = `${article?.title?.replace(/[^a-z0-9]/gi, '_').toLowerCase() || 'chunks'}_index.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const downloadArticleAsJson = () => {
    const articleData = {
      id: article?.id,
      title: article?.title,
      url: article?.url,
      lang: article?.lang,
      created_at: article?.created_at,
      stats: article?.stats,
      options: article?.options,
      metadata: {
        export_date: new Date().toISOString()
      }
    }
    
    const dataStr = JSON.stringify(articleData, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    
    const link = document.createElement('a')
    link.href = url
    link.download = `${article?.title?.replace(/[^a-z0-9]/gi, '_').toLowerCase() || 'article'}_article.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  if (articleLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-500 border-t-transparent mx-auto"></div>
          <p className="mt-4 text-gray-400">Loading article...</p>
        </div>
      </div>
    )
  }

  if (!article) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-white mb-4">
            Article not found
          </h1>
          <Link 
            to="/" 
            className="inline-flex items-center text-blue-400 hover:text-blue-300 font-medium"
          >
            <ChevronLeftIcon className="h-4 w-4 mr-1" />
            Back to home
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <div className="max-w-6xl mx-auto px-6 py-8 space-y-8">
        {/* Breadcrumb */}
        <nav className="flex items-center space-x-2 text-sm">
          <Link 
            to="/" 
            className="text-gray-400 hover:text-gray-300 transition-colors"
          >
            Home
          </Link>
          <span className="text-gray-600">/</span>
          <span className="text-white font-medium truncate">
            {article.title}
          </span>
        </nav>

        {/* Article Header */}
        <div className="bg-gray-800 rounded-2xl border border-gray-700 overflow-hidden">
          <div className="p-8">
            <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
              <div className="flex-1 min-w-0">
                <h1 className="text-3xl font-semibold text-white mb-4 leading-tight">
                  {article.title}
                </h1>
                <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-gray-400">
                  <span className="flex items-center">
                    <span className="font-medium">Language:</span> 
                    <span className="ml-1">{article.lang}</span>
                  </span>
                  <span className="flex items-center">
                    <span className="font-medium">Created:</span> 
                    <span className="ml-1">{new Date(article.created_at).toLocaleDateString()}</span>
                  </span>
                  <span className="flex items-center">
                    <span className="font-medium">Words:</span> 
                    <span className="ml-1">{article.stats.word_count?.toLocaleString()}</span>
                  </span>
                  <span className="flex items-center">
                    <span className="font-medium">Chunks:</span> 
                    <span className="ml-1">{article.stats.num_chunks}</span>
                  </span>
                </div>
                
                {/* Article URL */}
                <div className="mt-4">
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 text-sm break-all transition-colors"
                  >
                    {article.url}
                  </a>
                </div>
              </div>
              
              <div className="flex flex-row lg:flex-col gap-3">
                <button
                  onClick={downloadArticleAsJson}
                  className="inline-flex items-center justify-center px-4 py-2 border border-gray-600 text-sm font-medium rounded-xl text-gray-200 bg-gray-700 hover:bg-gray-600 transition-colors"
                >
                  <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
                  Download Article
                </button>
                <Link
                  to={`/dataset/${article.id}`}
                  className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-xl text-white bg-blue-600 hover:bg-blue-700 transition-colors"
                >
                  <DocumentTextIcon className="h-4 w-4 mr-2" />
                  View Questions
                </Link>
              </div>
            </div>

            {/* Processing Options */}
            <div className="mt-8 p-6 bg-gray-700 rounded-xl">
              <h3 className="text-sm font-medium text-white mb-4">
                Processing Configuration
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="text-sm">
                  <span className="block text-gray-400">Chunk Size</span>
                  <span className="font-medium text-white">{article.options.chunk_size}</span>
                </div>
                <div className="text-sm">
                  <span className="block text-gray-400">Strategy</span>
                  <span className="font-medium text-white">{article.options.split_strategy}</span>
                </div>
                <div className="text-sm">
                  <span className="block text-gray-400">Questions</span>
                  <span className="font-medium text-white">{article.options.total_questions}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Chunks Section */}
        <div className="bg-gray-800 rounded-2xl border border-gray-700 overflow-hidden">
          <div className="p-8">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
              <h2 className="text-xl font-medium text-white">
                Chunks ({chunks.length})
              </h2>
              <button
                onClick={downloadChunksAsJson}
                className="text-sm text-blue-400 hover:text-blue-300 font-medium self-start sm:self-auto"
              >
                Download Index (JSON)
              </button>
            </div>

            {/* Search */}
            <div className="mb-6">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search chunks..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-600 bg-gray-700 text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {chunksLoading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-6 w-6 border-2 border-blue-500 border-t-transparent mx-auto"></div>
                <p className="mt-3 text-sm text-gray-400">Loading chunks...</p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredChunks.map((chunk) => (
                  <div key={chunk.id} className="border border-gray-600 rounded-xl overflow-hidden hover:shadow-sm transition-shadow">
                    <div className="p-6">
                      <div className="flex-1 min-w-0">
                        <div className="flex flex-wrap items-center gap-3 mb-4">
                          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-900 text-blue-200">
                            {chunk.id}
                          </span>
                          <span className="text-sm text-gray-400">
                            {chunk.heading_path}
                          </span>
                        </div>
                        
                        <div className="bg-gray-700 rounded-lg p-4 mb-4 max-h-80 overflow-y-auto">
                          <pre className="whitespace-pre-wrap text-sm text-white font-mono leading-relaxed">
                            {chunk.content}
                          </pre>
                        </div>
                        
                        <div className="flex flex-wrap items-center gap-4 text-xs text-gray-400">
                          <span>{chunk.char_count} characters</span>
                          <span>•</span>
                          <span>~{chunk.token_estimate} tokens</span>
                          <span>•</span>
                          <span>Position: {chunk.start_char}-{chunk.end_char}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                
                {filteredChunks.length === 0 && searchQuery && (
                  <div className="text-center py-12">
                    <MagnifyingGlassIcon className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                    <p className="text-gray-400">
                      No chunks found matching "{searchQuery}"
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ArticlePage 