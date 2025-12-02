import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { 
  DocumentTextIcon,
  DocumentArrowDownIcon,
  MagnifyingGlassIcon,
  ChevronLeftIcon,
  DocumentIcon,
} from '@heroicons/react/24/outline'

import { getArticle, getChunks, getFileUrl, downloadFile, getDataset } from '../lib/api'

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

  const downloadArticleAsJson = async () => {
    try {
      // Fetch the article content and dataset in parallel
      const [articleBlob, dataset] = await Promise.all([
        downloadFile(article!.id, 'article.md'),
        getDataset(article!.id)
      ])
      
      const articleContent = await articleBlob.text()
      
      const comprehensiveData = {
        article: {
          id: article?.id,
          title: article?.title,
          url: article?.url,
          lang: article?.lang,
          created_at: article?.created_at,
          stats: article?.stats,
          options: article?.options,
          content: articleContent
        },
        chunks: chunks,
        questions: {
          total_questions: dataset.total_questions,
          items: dataset.items
        },
        metadata: {
          export_date: new Date().toISOString(),
          content_format: 'markdown',
          total_chunks: chunks.length,
          description: 'Complete article dataset including content, chunks, and generated questions'
        }
      }
      
      const dataStr = JSON.stringify(comprehensiveData, null, 2)
      const dataBlob = new Blob([dataStr], { type: 'application/json' })
      const url = URL.createObjectURL(dataBlob)
      
      const link = document.createElement('a')
      link.href = url
      link.download = `${article?.title?.replace(/[^a-z0-9]/gi, '_').toLowerCase() || 'article'}_complete.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to download complete article data:', error)
      // Fallback to article and chunks only if dataset fetch fails
      try {
        const articleBlob = await downloadFile(article!.id, 'article.md')
        const articleContent = await articleBlob.text()
        
        const fallbackData = {
          article: {
            id: article?.id,
            title: article?.title,
            url: article?.url,
            lang: article?.lang,
            created_at: article?.created_at,
            stats: article?.stats,
            options: article?.options,
            content: articleContent
          },
          chunks: chunks,
          metadata: {
            export_date: new Date().toISOString(),
            content_format: 'markdown',
            total_chunks: chunks.length,
            error: 'Questions could not be fetched'
          }
        }
        
        const dataStr = JSON.stringify(fallbackData, null, 2)
        const dataBlob = new Blob([dataStr], { type: 'application/json' })
        const url = URL.createObjectURL(dataBlob)
        
        const link = document.createElement('a')
        link.href = url
        link.download = `${article?.title?.replace(/[^a-z0-9]/gi, '_').toLowerCase() || 'article'}_partial.json`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
      } catch (fallbackError) {
        console.error('Fallback download also failed:', fallbackError)
        // Final fallback with metadata only
        const metadataOnlyData = {
          article: {
            id: article?.id,
            title: article?.title,
            url: article?.url,
            lang: article?.lang,
            created_at: article?.created_at,
            stats: article?.stats,
            options: article?.options
          },
          metadata: {
            export_date: new Date().toISOString(),
            error: 'Content and questions could not be fetched'
          }
        }
        
        const dataStr = JSON.stringify(metadataOnlyData, null, 2)
        const dataBlob = new Blob([dataStr], { type: 'application/json' })
        const url = URL.createObjectURL(dataBlob)
        
        const link = document.createElement('a')
        link.href = url
        link.download = `${article?.title?.replace(/[^a-z0-9]/gi, '_').toLowerCase() || 'article'}_metadata.json`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
      }
    }
  }

  const downloadArticleMarkdown = async () => {
    try {
      const articleBlob = await downloadFile(article!.id, 'article.md')
      const url = URL.createObjectURL(articleBlob)
      
      const link = document.createElement('a')
      link.href = url
      link.download = `${article?.title?.replace(/[^a-z0-9]/gi, '_').toLowerCase() || 'article'}.md`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to download markdown:', error)
    }
  }

  if (articleLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-gray-900 border-t-transparent mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading article...</p>
        </div>
      </div>
    )
  }

  if (!article) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-black mb-4">
            Article not found
          </h1>
          <Link 
            to="/" 
            className="inline-flex items-center text-gray-700 hover:text-black font-medium"
          >
            <ChevronLeftIcon className="h-4 w-4 mr-1" />
            Back to home
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-6xl mx-auto px-6 py-8 space-y-8">
        {/* Breadcrumb */}
        <nav className="flex items-center space-x-2 text-sm">
          <Link 
            to="/" 
            className="text-gray-600 hover:text-gray-900 transition-colors"
          >
            Home
          </Link>
          <span className="text-gray-400">/</span>
          <span className="text-black font-medium truncate">
            {article.title}
          </span>
        </nav>

        {/* Article Header */}
        <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
          <div className="p-8">
            <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
              <div className="flex-1 min-w-0">
                <h1 className="text-3xl font-semibold text-black mb-4 leading-tight">
                  {article.title}
                </h1>
                <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-gray-600">
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
                    className="text-gray-700 hover:text-black text-sm break-all transition-colors underline"
                  >
                    {article.url}
                  </a>
                </div>
              </div>
              
              <div className="flex flex-row lg:flex-col gap-3">
                <button
                  onClick={downloadArticleAsJson}
                  className="inline-flex items-center justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-xl text-gray-700 bg-white hover:bg-gray-50 transition-colors"
                >
                  <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
                  Download Article
                </button>
                <Link
                  to={`/dataset/${article.id}`}
                  className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-xl text-white bg-black hover:bg-gray-800 transition-colors"
                >
                  <DocumentTextIcon className="h-4 w-4 mr-2" />
                  View Questions
                </Link>
                <button
                  onClick={downloadArticleMarkdown}
                  className="inline-flex items-center justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-xl text-gray-700 bg-white hover:bg-gray-50 transition-colors"
                >
                  <DocumentIcon className="h-4 w-4 mr-2" />
                  Download Markdown
                </button>
              </div>
            </div>

            {/* Processing Options */}
            <div className="mt-8 p-6 bg-gray-100 rounded-xl">
              <h3 className="text-sm font-medium text-black mb-4">
                Processing Configuration
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="text-sm">
                  <span className="block text-gray-600">Chunk Size</span>
                  <span className="font-medium text-black">{article.options.chunk_size}</span>
                </div>
                <div className="text-sm">
                  <span className="block text-gray-600">Strategy</span>
                  <span className="font-medium text-black">{article.options.split_strategy}</span>
                </div>
                <div className="text-sm">
                  <span className="block text-gray-600">Questions</span>
                  <span className="font-medium text-black">{article.options.total_questions}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Chunks Section */}
        <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
          <div className="p-8">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
              <h2 className="text-xl font-medium text-black">
                Chunks ({chunks.length})
              </h2>
              <button
                onClick={downloadChunksAsJson}
                className="text-sm text-gray-900 hover:text-gray-700 font-medium self-start sm:self-auto"
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
                  className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-300 bg-white text-black placeholder-gray-400 focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                />
              </div>
            </div>

            {chunksLoading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-6 w-6 border-2 border-gray-900 border-t-transparent mx-auto"></div>
                <p className="mt-3 text-sm text-gray-600">Loading chunks...</p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredChunks.map((chunk) => (
                  <div key={chunk.id} className="border border-gray-200 rounded-xl overflow-hidden hover:shadow-sm transition-shadow">
                    <div className="p-6">
                      <div className="flex-1 min-w-0">
                        <div className="flex flex-wrap items-center gap-3 mb-4">
                          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-900 text-white">
                            {chunk.id}
                          </span>
                          <span className="text-sm text-gray-600">
                            {chunk.heading_path}
                          </span>
                        </div>
                        
                        <div className="bg-gray-50 rounded-lg p-4 mb-4 max-h-80 overflow-y-auto border border-gray-200">
                          <pre className="whitespace-pre-wrap text-sm text-black font-mono leading-relaxed">
                            {chunk.content}
                          </pre>
                        </div>
                        
                        <div className="flex flex-wrap items-center gap-4 text-xs text-gray-600">
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
                    <MagnifyingGlassIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">
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