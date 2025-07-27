import React, { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import JSZip from 'jszip'
import { 
  DocumentTextIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ArrowPathIcon,
  TrashIcon,
  RectangleStackIcon,
  ChatBubbleLeftRightIcon,
  ArrowDownTrayIcon,
} from '@heroicons/react/24/outline'

import { startIngestion, getArticles, deleteArticle, downloadFile, getDataset, getChunks } from '../lib/api'
import { useIngestStream } from '../hooks/useIngestStream'
import type { IngestOptions } from '../types/api'

function HomePage() {
  const [url, setUrl] = useState('')
  const [currentRunId, setCurrentRunId] = useState<string | null>(null)
  const [isLoadingRandomArticle, setIsLoadingRandomArticle] = useState(false)
  const [selectedArticles, setSelectedArticles] = useState<string[]>([])
  const [options, setOptions] = useState<Partial<IngestOptions>>({
    chunk_size: 1000,
    chunk_overlap: 200,
    split_strategy: 'header_aware',
    total_questions: 2,
    llm_model: 'gpt-4o-mini',
    reingest: false,
  })

  const { data: articles = [], refetch: refetchArticles } = useQuery({
    queryKey: ['articles'],
    queryFn: getArticles,
  })

  const { events, isConnected, error, lastEvent } = useIngestStream(currentRunId)

  const ingestMutation = useMutation({
    mutationFn: startIngestion,
    onSuccess: (data) => {
      setCurrentRunId(data.run_id)
      if (data.status === 'existing') {
        toast.success('Article already exists!')
        refetchArticles()
      }
    },
    onError: (error) => {
      toast.error(`Failed to start ingestion: ${error.message}`)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: deleteArticle,
    onSuccess: () => {
      toast.success('Article deleted successfully!')
      refetchArticles()
    },
    onError: (error) => {
      toast.error(`Failed to delete article: ${error.message}`)
    },
  })

  const handleDeleteArticle = (articleId: string, articleTitle: string) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${articleTitle}"? This will permanently remove the article and all related files including chunks and dataset.`
    )
    
    if (confirmed) {
      deleteMutation.mutate(articleId)
    }
  }

  const handleDownloadArticle = async (articleId: string, articleTitle: string) => {
    try {
      toast.loading('Downloading article...')
      const blob = await downloadFile(articleId, 'article.md')
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      
      // Create safe filename
      const safeTitle = articleTitle.replace(/[^a-zA-Z0-9_-]/g, '_').toLowerCase()
      link.download = `${safeTitle}_article.md`
      
      // Trigger download
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      toast.dismiss()
      toast.success('Article downloaded successfully!')
    } catch (error) {
      toast.dismiss()
      toast.error(`Failed to download article: ${error.message}`)
      console.error('Download error:', error)
    }
  }

  const handleArticleSelection = (articleId: string) => {
    setSelectedArticles(prev => 
      prev.includes(articleId) 
        ? prev.filter(id => id !== articleId)
        : [...prev, articleId]
    )
  }

  const handleSelectAll = () => {
    if (selectedArticles.length === articles.length) {
      setSelectedArticles([])
    } else {
      setSelectedArticles(articles.map(article => article.id))
    }
  }

  const handleDownloadAllArticles = async () => {
    if (selectedArticles.length === 0) {
      toast.error('No articles selected for download')
      return
    }

    const selectedArticlesList = articles.filter(article => selectedArticles.includes(article.id))

    try {
      toast.loading(`Downloading ${selectedArticles.length} complete article datasets...`)
      
      // Download selected articles with complete data in parallel
      const downloadPromises = selectedArticlesList.map(async (article) => {
        try {
          // Fetch article content, chunks, and dataset in parallel
          const [articleBlob, chunks, dataset] = await Promise.all([
            downloadFile(article.id, 'article.md'),
            getChunks(article.id),
            getDataset(article.id)
          ])
          
          const articleContent = await articleBlob.text()
          
          const comprehensiveData = {
            article: {
              id: article.id,
              title: article.title,
              url: article.url,
              lang: article.lang,
              created_at: article.created_at,
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
          const safeTitle = article.title.replace(/[^a-zA-Z0-9_-]/g, '_').toLowerCase()
          
          return {
            blob: dataBlob,
            filename: `${safeTitle}_complete.json`,
            title: article.title
          }
        } catch (error) {
          // Fallback to article content only if dataset/chunks fetch fails
          try {
            const articleBlob = await downloadFile(article.id, 'article.md')
            const articleContent = await articleBlob.text()
            
            const fallbackData = {
              article: {
                id: article.id,
                title: article.title,
                url: article.url,
                lang: article.lang,
                created_at: article.created_at,
                content: articleContent
              },
              metadata: {
                export_date: new Date().toISOString(),
                content_format: 'markdown',
                error: 'Chunks and questions could not be fetched'
              }
            }
            
            const dataStr = JSON.stringify(fallbackData, null, 2)
            const dataBlob = new Blob([dataStr], { type: 'application/json' })
            const safeTitle = article.title.replace(/[^a-zA-Z0-9_-]/g, '_').toLowerCase()
            
            return {
              blob: dataBlob,
              filename: `${safeTitle}_partial.json`,
              title: article.title
            }
          } catch (fallbackError) {
            // Final fallback with metadata only
            const metadataOnlyData = {
              article: {
                id: article.id,
                title: article.title,
                url: article.url,
                lang: article.lang,
                created_at: article.created_at
              },
              metadata: {
                export_date: new Date().toISOString(),
                error: 'Content and questions could not be fetched'
              }
            }
            
            const dataStr = JSON.stringify(metadataOnlyData, null, 2)
            const dataBlob = new Blob([dataStr], { type: 'application/json' })
            const safeTitle = article.title.replace(/[^a-zA-Z0-9_-]/g, '_').toLowerCase()
            
            return {
              blob: dataBlob,
              filename: `${safeTitle}_metadata.json`,
              title: article.title
            }
          }
        }
      })

      const downloads = await Promise.all(downloadPromises)
      
      // Create ZIP file containing all JSON files
      const zip = new JSZip()
      
      // Add each JSON file to the ZIP
      downloads.forEach(({ blob, filename }) => {
        zip.file(filename, blob)
      })
      
      // Generate ZIP file
      const zipBlob = await zip.generateAsync({ type: 'blob' })
      
      // Create safe filename for the ZIP
      const currentDate = new Date().toISOString().split('T')[0]
      const zipFilename = `articles_export_${currentDate}_${downloads.length}_files.zip`
      
      // Download ZIP file
      const url = window.URL.createObjectURL(zipBlob)
      const link = document.createElement('a')
      link.href = url
      link.download = zipFilename
      
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      toast.dismiss()
      toast.success(`Successfully downloaded ZIP file with ${downloads.length} complete datasets!`)
    } catch (error) {
      toast.dismiss()
      toast.error(`Failed to download articles: ${error.message}`)
      console.error('Bulk download error:', error)
    }
  }

  const fetchRandomArticle = async () => {
    setIsLoadingRandomArticle(true)
    try {
      // Use Wikipedia's random page API
      const response = await fetch('https://en.wikipedia.org/api/rest_v1/page/random/summary')
      if (!response.ok) {
        throw new Error('Failed to fetch random article')
      }
      const data = await response.json()
      const randomUrl = `https://en.wikipedia.org/wiki/${encodeURIComponent(data.title.replace(/ /g, '_'))}`
      setUrl(randomUrl)
      toast.success('Random article suggested!')
    } catch (error) {
      toast.error('Failed to fetch random article')
      console.error('Random article fetch error:', error)
    } finally {
      setIsLoadingRandomArticle(false)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!url.trim()) {
      toast.error('Please enter a Wikipedia URL')
      return
    }

    ingestMutation.mutate({
      wikipedia_url: url,
      options,
    })
  }

  const isProcessing = currentRunId && isConnected
  const isDone = lastEvent?.stage === 'DONE'
  const isFailed = lastEvent?.stage === 'FAILED'

  // Reset state when done or failed
  if (isDone || isFailed) {
    if (currentRunId && !isConnected) {
      setTimeout(() => {
        setCurrentRunId(null)
        if (isDone) {
          refetchArticles()
          setUrl('')
          toast.success('Article processing completed!')
        }
      }, 2000)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <div className="max-w-5xl mx-auto px-6 py-12 space-y-12">
        {/* Header */}
        <div className="text-center space-y-3">
          <h1 className="text-4xl font-semibold text-white tracking-tight">
            RAG Dataset Creator
          </h1>
          <p className="text-lg text-gray-400 font-light">
            Transform Wikipedia articles into structured Q&A datasets
          </p>
        </div>

        {/* URL Input Form */}
        <div className="bg-gray-800 rounded-2xl border border-gray-700 overflow-hidden">
          <div className="p-8">
            <h2 className="text-xl font-medium text-white mb-6">
              Add Wikipedia Article
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="url" className="block text-sm font-medium text-gray-300 mb-3">
                  Wikipedia URL
                </label>
                <div className="flex rounded-xl border border-gray-600 overflow-hidden focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-transparent">
                  <input
                    type="url"
                    id="url"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://en.wikipedia.org/wiki/Machine_learning"
                    className="flex-1 px-4 py-3 border-0 bg-transparent text-white placeholder-gray-400 focus:ring-0 focus:outline-none"
                    disabled={isProcessing}
                  />
                  <button
                    type="button"
                    onClick={fetchRandomArticle}
                    disabled={isProcessing || isLoadingRandomArticle}
                    className="px-4 py-3 text-gray-400 hover:text-gray-200 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    title="Suggest random Wikipedia article"
                  >
                    <ArrowPathIcon className={`h-5 w-5 ${isLoadingRandomArticle ? 'animate-spin' : ''}`} />
                  </button>
                </div>
                <p className="mt-2 text-xs text-gray-400">
                  Click the refresh icon to get a random Wikipedia article suggestion
                </p>
              </div>

              {/* Options */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Chunk Size
                  </label>
                  <input
                    type="number"
                    min="100"
                    max="5000"
                    value={options.chunk_size}
                    onChange={(e) => setOptions(prev => ({ ...prev, chunk_size: parseInt(e.target.value) }))}
                    className="w-full px-3 py-2 rounded-lg border border-gray-600 bg-gray-700 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    disabled={isProcessing}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Total Questions
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="50"
                    value={options.total_questions}
                    onChange={(e) => setOptions(prev => ({ ...prev, total_questions: parseInt(e.target.value) }))}
                    className="w-full px-3 py-2 rounded-lg border border-gray-600 bg-gray-700 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    disabled={isProcessing}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Split Strategy
                  </label>
                  <select
                    value={options.split_strategy}
                    onChange={(e) => setOptions(prev => ({ ...prev, split_strategy: e.target.value as 'recursive' | 'sentence' | 'header_aware' }))}
                    className="w-full h-10 px-3 py-2 rounded-lg border border-gray-600 bg-gray-700 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    disabled={isProcessing}
                  >
                    <option value="recursive">Recursive</option>
                    <option value="sentence">Sentence</option>
                    <option value="header_aware">Header Aware</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                disabled={isProcessing || !url.trim()}
                className="w-full py-3 px-6 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-medium rounded-xl transition-colors disabled:cursor-not-allowed focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-800"
              >
                {isProcessing ? 'Processing...' : 'Process Article'}
              </button>
            </form>
          </div>
        </div>

        {/* Progress Display */}
        {currentRunId && (
          <div className="bg-gray-800 rounded-2xl border border-gray-700 overflow-hidden animate-fade-in">
            <div className="p-8">
              <h3 className="text-xl font-medium text-white mb-6">
                Processing Progress
              </h3>
              
              {/* Single Progress Row */}
              {events.length > 0 && (
                <div className="space-y-4">
                  {/* Progress Bar */}
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-500 ${
                        lastEvent?.stage === 'FAILED' ? 'bg-red-500' : 
                        lastEvent?.stage === 'DONE' ? 'bg-green-500' : 'bg-blue-500'
                      }`}
                      style={{ width: `${(events.length / (events.length + (lastEvent?.stage === 'DONE' ? 0 : 1))) * 100}%` }}
                    />
                  </div>
                  
                  {/* Current Step */}
                  <div className="flex items-center space-x-4 p-4 rounded-xl bg-gray-700">
                    <div className="flex-shrink-0">
                      {lastEvent?.stage === 'FAILED' ? (
                        <ExclamationCircleIcon className="h-5 w-5 text-red-500" />
                      ) : lastEvent?.stage === 'DONE' ? (
                        <CheckCircleIcon className="h-5 w-5 text-green-500" />
                      ) : (
                        <div className="flex items-center space-x-2">
                          <ClockIcon className="h-5 w-5 text-blue-500" />
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                        </div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <p className="text-sm font-medium text-white">
                          {lastEvent?.stage || 'Starting...'}
                        </p>
                        <span className="text-xs text-gray-400">
                          ({events.length} step{events.length !== 1 ? 's' : ''} completed)
                        </span>
                      </div>
                      <p className="text-sm text-gray-300 mt-1">
                        {lastEvent?.message || 'Initializing...'}
                      </p>
                    </div>
                    <div className="text-xs text-gray-400 flex-shrink-0">
                      {lastEvent && new Date(lastEvent.timestamp * 1000).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              )}

              {error && (
                <div className="mt-6 p-4 bg-red-900/20 border border-red-800 rounded-xl">
                  <p className="text-sm text-red-400">
                    Connection error: {error}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Articles List */}
        <div className="bg-gray-800 rounded-2xl border border-gray-700 overflow-hidden">
          <div className="p-8">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-4">
                <h2 className="text-xl font-medium text-white">
                  Recent Articles
                </h2>
                {articles.length > 0 && (
                  <button
                    onClick={handleSelectAll}
                    className="text-sm text-blue-400 hover:text-blue-300 font-medium"
                  >
                    {selectedArticles.length === articles.length ? 'Deselect All' : 'Select All'}
                  </button>
                )}
              </div>
              <button
                onClick={handleDownloadAllArticles}
                disabled={selectedArticles.length === 0}
                className="flex items-center space-x-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white text-sm font-medium rounded-lg transition-colors disabled:cursor-not-allowed focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-gray-800"
                title={`Download ${selectedArticles.length} selected articles`}
              >
                <ArrowDownTrayIcon className="h-4 w-4" />
                <span>Download Selected ({selectedArticles.length})</span>
              </button>
            </div>
            
            {articles.length === 0 ? (
              <div className="text-center py-16">
                <DocumentTextIcon className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400">
                  No articles processed yet. Add a Wikipedia URL above to get started.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {articles.slice(0, 10).map((article) => (
                  <div 
                    key={article.id} 
                    onClick={() => handleArticleSelection(article.id)}
                    className={`group flex items-center justify-between p-4 rounded-xl border transition-colors cursor-pointer ${
                      selectedArticles.includes(article.id) 
                        ? 'border-blue-500 bg-blue-900/20' 
                        : 'border-gray-700 hover:bg-gray-700'
                    }`}
                  >
                    <div className="flex items-center space-x-4 min-w-0 flex-1">
                      <div className="flex-shrink-0">
                        <input
                          type="checkbox"
                          checked={selectedArticles.includes(article.id)}
                          onChange={(e) => {
                            e.stopPropagation()
                            handleArticleSelection(article.id)
                          }}
                          onClick={(e) => e.stopPropagation()}
                          className="h-4 w-4 rounded border-gray-600 bg-gray-700 text-blue-600 focus:ring-blue-500 focus:ring-offset-0"
                        />
                      </div>
                      <div className="flex-shrink-0">
                        <DocumentTextIcon className="h-5 w-5 text-gray-400" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <h3 className="text-sm font-medium text-white truncate">
                          {article.title}
                        </h3>
                        <p className="text-xs text-gray-400 mt-1">
                          {article.lang} • {new Date(article.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3 opacity-70 group-hover:opacity-100 transition-opacity">
                      <Link
                        to={`/articles/${article.id}`}
                        onClick={(e) => e.stopPropagation()}
                        className="text-sm text-blue-400 hover:text-blue-300 flex items-center space-x-1 font-medium"
                      >
                        <RectangleStackIcon className="h-4 w-4" />
                        <span>Chunks</span>
                      </Link>
                      <Link
                        to={`/dataset/${article.id}`}
                        onClick={(e) => e.stopPropagation()}
                        className="text-sm text-green-400 hover:text-green-300 flex items-center space-x-1 font-medium"
                      >
                        <ChatBubbleLeftRightIcon className="h-4 w-4" />
                        <span>Question</span>
                      </Link>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDeleteArticle(article.id, article.title)
                        }}
                        disabled={deleteMutation.isPending}
                        className="text-sm text-red-400 hover:text-red-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1 font-medium"
                        title="Delete article"
                      >
                        <TrashIcon className="h-4 w-4" />
                        <span>Delete</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomePage 