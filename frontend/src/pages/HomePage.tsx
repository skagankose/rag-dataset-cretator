import React, { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { 
  DocumentTextIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ArrowPathIcon,
  TrashIcon,
} from '@heroicons/react/24/outline'

import { startIngestion, getArticles, deleteArticle } from '../lib/api'
import { useIngestStream } from '../hooks/useIngestStream'
import type { IngestOptions } from '../types/api'

function HomePage() {
  const [url, setUrl] = useState('')
  const [currentRunId, setCurrentRunId] = useState<string | null>(null)
  const [isLoadingRandomArticle, setIsLoadingRandomArticle] = useState(false)
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
                    className="w-full px-3 py-2 rounded-lg border border-gray-600 bg-gray-700 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none h-10"
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
              
              <div className="space-y-4">
                {events.map((event, index) => (
                  <div key={index} className="flex items-start space-x-4 p-4 rounded-xl bg-gray-700">
                    <div className="flex-shrink-0 mt-0.5">
                      {event.stage === 'FAILED' ? (
                        <ExclamationCircleIcon className="h-5 w-5 text-red-500" />
                      ) : event.stage === 'DONE' ? (
                        <CheckCircleIcon className="h-5 w-5 text-green-500" />
                      ) : (
                        <ClockIcon className="h-5 w-5 text-blue-500" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-white">
                        {event.stage}
                      </p>
                      <p className="text-sm text-gray-300 mt-1">
                        {event.message}
                      </p>
                    </div>
                    <div className="text-xs text-gray-400 flex-shrink-0">
                      {new Date(event.timestamp * 1000).toLocaleTimeString()}
                    </div>
                  </div>
                ))}
              </div>

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
            <h2 className="text-xl font-medium text-white mb-6">
              Recent Articles
            </h2>
            
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
                  <div key={article.id} className="group flex items-center justify-between p-4 rounded-xl border border-gray-700 hover:bg-gray-700 transition-colors">
                    <div className="flex items-center space-x-4 min-w-0 flex-1">
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
                        className="text-sm text-blue-400 hover:text-blue-300 font-medium"
                      >
                        View
                      </Link>
                      <Link
                        to={`/dataset/${article.id}`}
                        className="text-sm text-blue-400 hover:text-blue-300 font-medium"
                      >
                        Dataset
                      </Link>
                      <button
                        onClick={() => handleDeleteArticle(article.id, article.title)}
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