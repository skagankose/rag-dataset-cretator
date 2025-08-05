import React, { useState, useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
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
  ChevronLeftIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline'

import { startIngestion, getArticles, deleteArticle, downloadFile, getDataset, getChunks } from '../lib/api'
import { useIngestStream } from '../hooks/useIngestStream'
import type { IngestOptions } from '../types/api'

function HomePage() {
  const [url, setUrl] = useState('')
  const [bulkUrls, setBulkUrls] = useState('')
  const [randomArticleCount, setRandomArticleCount] = useState(5)
  const [currentRunId, setCurrentRunId] = useState<string | null>(null)
  const [isLoadingRandomArticle, setIsLoadingRandomArticle] = useState(false)
  const [isLoadingRandomBulk, setIsLoadingRandomBulk] = useState(false)
  const [selectedArticles, setSelectedArticles] = useState<string[]>([])
  const [bulkProcessing, setBulkProcessing] = useState(false)
  const [bulkProgress, setBulkProgress] = useState({ 
    submitted: 0, 
    completed: 0, 
    total: 0, 
    currentUrl: '',
    processingArticles: new Map()
  })
  const [shouldStopBulkProcessing, setShouldStopBulkProcessing] = useState(false)
  const [options, setOptions] = useState<Partial<IngestOptions>>({
    chunk_size: 1000,
    chunk_overlap: 200,
    split_strategy: 'header_aware',
    total_questions: 2,
    // llm_model will be set automatically by backend based on provider
    reingest: false,
  })

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage] = useState(10)

  const queryClient = useQueryClient()
  
  const { data: articles = [], refetch: refetchArticles } = useQuery({
    queryKey: ['articles'],
    queryFn: getArticles,
  })

  const { events, isConnected, error, lastEvent } = useIngestStream(currentRunId)

  // Pagination logic
  const totalPages = Math.ceil(articles.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentArticles = articles.slice(startIndex, endIndex)

  const goToPage = (page: number) => {
    setCurrentPage(page)
  }

  const goToPrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1)
    }
  }

  const goToNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1)
    }
  }

  // Reset to first page when articles change
  useEffect(() => {
    setCurrentPage(1)
  }, [articles.length])

  const ingestMutation = useMutation({
    mutationFn: startIngestion,
    onSuccess: (data) => {
      setCurrentRunId(data.run_id)
      if (data.status === 'existing') {
        toast.success('Article already exists!')
        queryClient.invalidateQueries({ queryKey: ['articles'] })
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
      
      // Create filename using article ID
      link.download = `${articleId}_article.md`
      
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

  const handleDeleteSelectedArticles = async () => {
    if (selectedArticles.length === 0) {
      toast.error('No articles selected for deletion')
      return
    }

    const selectedTitles = articles
      .filter(article => selectedArticles.includes(article.id))
      .map(article => article.title)
      .join(', ')

    const confirmed = window.confirm(
      `Are you sure you want to delete ${selectedArticles.length} selected article(s)?\n\n${selectedTitles}\n\nThis will permanently remove the articles and all related files including chunks and datasets.`
    )
    
    if (!confirmed) return

    try {
      toast.loading(`Deleting ${selectedArticles.length} articles...`)
      
      // Delete all selected articles in parallel
      const deletePromises = selectedArticles.map(articleId => 
        deleteMutation.mutateAsync(articleId)
      )

      await Promise.all(deletePromises)
      
      // Clear selection after successful deletion
      setSelectedArticles([])
      
      toast.dismiss()
      toast.success(`Successfully deleted ${selectedArticles.length} articles!`)
      refetchArticles()
    } catch (error) {
      toast.dismiss()
      toast.error(`Failed to delete some articles: ${error.message}`)
      console.error('Bulk delete error:', error)
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
          return {
            blob: dataBlob,
            filename: `${article.id}.json`,
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
            return {
              blob: dataBlob,
              filename: `${article.id}_partial.json`,
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
            return {
              blob: dataBlob,
              filename: `${article.id}_metadata.json`,
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

  const handleStopBulkProcessing = () => {
    setShouldStopBulkProcessing(true)
    setBulkProcessing(false)
    setBulkProgress({ 
      submitted: 0, 
      completed: 0, 
      total: 0, 
      currentUrl: '',
      processingArticles: new Map()
    })
    setShouldStopBulkProcessing(false)
    
    // Refresh the page to ensure clean state
    window.location.reload()
  }

  const handleBulkProcessing = async () => {
    if (bulkProcessing) {
      toast.error('Bulk processing is already in progress')
      return
    }

    if (!bulkUrls.trim()) {
      toast.error('Please enter Wikipedia URLs')
      return
    }

    // Parse URLs from comma-separated input
    const urls = bulkUrls
      .split(',')
      .map(url => url.trim())
      .filter(url => url.length > 0)

    if (urls.length === 0) {
      toast.error('Please enter valid Wikipedia URLs')
      return
    }

    // Validate URLs format
    const invalidUrls = urls.filter(url => {
      try {
        const urlObj = new URL(url)
        return !urlObj.hostname.includes('wikipedia.org')
      } catch {
        return true
      }
    })

    if (invalidUrls.length > 0) {
      const firstInvalid = invalidUrls[0]
      toast.error(`Invalid Wikipedia URL found: "${firstInvalid}". Please ensure all URLs are valid Wikipedia links.`, { duration: 6000 })
      return
    }

    setBulkProcessing(true)
    setShouldStopBulkProcessing(false)
    setBulkProgress({ 
      submitted: 0, 
      completed: 0, 
      total: urls.length, 
      currentUrl: '',
      processingArticles: new Map()
    })

    try {
      let successCount = 0
      let errorCount = 0
      const processingArticles = new Map()

      // Step 1: Submit all articles for processing
      for (let i = 0; i < urls.length; i++) {
        // Check if user wants to stop processing
        if (shouldStopBulkProcessing) {
          toast.info('Bulk processing stopped by user')
          break
        }

        const currentUrl = urls[i]
        setBulkProgress(prev => ({ 
          ...prev, 
          submitted: i + 1, 
          currentUrl: `Submitting: ${currentUrl}` 
        }))

        try {
          const response = await startIngestion({
            wikipedia_url: currentUrl,
            options,
          })

          if (response.status === 'started') {
            processingArticles.set(response.run_id, {
              url: currentUrl,
              status: 'processing',
              runId: response.run_id,
              startTime: Date.now()
            })
            successCount++
          } else if (response.status === 'existing') {
            successCount++
            setBulkProgress(prev => ({ 
              ...prev, 
              completed: prev.completed + 1 
            }))
          } else if (response.status === 'failed') {
            // Handle explicit failure status from backend
            console.error(`Backend reported failure for ${currentUrl}:`, response.message || 'Unknown error')
            errorCount++
            setBulkProgress(prev => ({ 
              ...prev, 
              completed: prev.completed + 1,
              currentUrl: `Failed: ${currentUrl} - ${response.message || 'Article may not exist'}`
            }))
          }
        } catch (error) {
          console.error(`Failed to process ${currentUrl}:`, error)
          
          // Determine error type for better user feedback
          let errorMessage = 'Unknown error'
          if (error.message) {
            if (error.message.includes('404') || error.message.includes('not found')) {
              errorMessage = 'Article not found'
            } else if (error.message.includes('network') || error.message.includes('fetch')) {
              errorMessage = 'Network error'
            } else if (error.message.includes('timeout')) {
              errorMessage = 'Request timeout'
            } else {
              errorMessage = error.message
            }
          }
          
          errorCount++
          setBulkProgress(prev => ({ 
            ...prev, 
            completed: prev.completed + 1,
            currentUrl: `Failed: ${currentUrl} - ${errorMessage}`
          }))
        }

        // Small delay between requests
        if (i < urls.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 500))
        }
      }

      // Step 2: Monitor processing completion with timeout handling
      const monitorCompletion = () => {
        return new Promise((resolve) => {
          const startTime = Date.now()
          const maxTimeout = 300000 // 5 minutes total timeout
          const articleTimeout = 60000 // 1 minute per article timeout

          const checkInterval = setInterval(async () => {
            // Check if user wants to stop processing
            if (shouldStopBulkProcessing) {
              clearInterval(checkInterval)
              resolve(null)
              return
            }

            const activeProcessing = Array.from(processingArticles.values())
              .filter(article => article.status === 'processing')

            if (activeProcessing.length === 0) {
              clearInterval(checkInterval)
              resolve(null)
              return
            }

            // Check for articles that have been processing too long (likely failed)
            const now = Date.now()
            let timedOutArticles = 0

            processingArticles.forEach((article, runId) => {
              if (article.status === 'processing') {
                const processingTime = now - (article.startTime || now)
                
                // If article has been processing for more than 1 minute, consider it failed
                if (processingTime > articleTimeout) {
                  console.warn(`Article timed out after ${processingTime}ms: ${article.url}`)
                  article.status = 'failed'
                  article.error = 'Processing timeout - article may not exist or failed to process'
                  timedOutArticles++
                  errorCount++
                }
              }
            })

            // Check articles list to see if new articles have appeared
            try {
              const currentArticles = await getArticles()
              let newCompletions = 0

              processingArticles.forEach((article, runId) => {
                if (article.status === 'processing') {
                  // Check if this article now exists in the articles list
                  const found = currentArticles.some(a => 
                    a.url === article.url || a.title.toLowerCase().includes(
                      article.url.split('/').pop()?.replace(/_/g, ' ').toLowerCase() || ''
                    )
                  )
                  
                  if (found) {
                    article.status = 'completed'
                    newCompletions++
                  }
                }
              })

              const totalNewCompletions = newCompletions + timedOutArticles
              if (totalNewCompletions > 0) {
                setBulkProgress(prev => ({ 
                  ...prev, 
                  completed: prev.completed + totalNewCompletions,
                  currentUrl: `Completed ${prev.completed + totalNewCompletions}/${prev.total} articles${timedOutArticles > 0 ? ` (${timedOutArticles} failed/timed out)` : ''}`
                }))
              }
            } catch (error) {
              console.error('Error checking article completion:', error)
            }

            // Global timeout - stop monitoring after 5 minutes regardless
            if (now - startTime > maxTimeout) {
              console.warn('Global timeout reached, stopping bulk processing monitor')
              
              // Mark any remaining processing articles as failed
              let remainingArticles = 0
              processingArticles.forEach((article, runId) => {
                if (article.status === 'processing') {
                  article.status = 'failed'
                  article.error = 'Global timeout reached'
                  remainingArticles++
                  errorCount++
                }
              })

              if (remainingArticles > 0) {
                setBulkProgress(prev => ({ 
                  ...prev, 
                  completed: prev.completed + remainingArticles,
                  currentUrl: `Timeout reached - marked ${remainingArticles} remaining articles as failed`
                }))
              }

              clearInterval(checkInterval)
              resolve(null)
              return
            }
          }, 2000) // Check every 2 seconds
        })
      }

      // Wait for all processing to complete
      if (processingArticles.size > 0) {
        setBulkProgress(prev => ({ 
          ...prev, 
          currentUrl: `Waiting for ${processingArticles.size} articles to complete processing...` 
        }))
        await monitorCompletion()
      }

      setBulkProcessing(false)
      setBulkProgress({ 
        submitted: 0, 
        completed: 0, 
        total: 0, 
        currentUrl: '',
        processingArticles: new Map()
      })

      // Count final results
      const totalProcessed = successCount + errorCount
      const actualSuccesses = Array.from(processingArticles.values())
        .filter(article => article.status === 'completed').length
      const actualFailures = Array.from(processingArticles.values())
        .filter(article => article.status === 'failed').length

      if (successCount > 0 || actualSuccesses > 0) {
        // Invalidate and refetch articles immediately
        queryClient.invalidateQueries({ queryKey: ['articles'] })
        
        // Poll for updates to ensure articles appear
        const pollForUpdates = async (attempts = 0) => {
          if (attempts < 10) { // Max 10 attempts (20 seconds)
            await new Promise(resolve => setTimeout(resolve, 2000))
            await refetchArticles()
            
            // Continue polling if needed
            setTimeout(() => pollForUpdates(attempts + 1), 2000)
          }
        }
        
        pollForUpdates()
        setBulkUrls('')
        
        // Provide detailed status message
        const totalErrors = errorCount + actualFailures
        if (totalErrors > 0) {
          toast.success(
            `Bulk processing completed! ${actualSuccesses || successCount} articles processed successfully. ${totalErrors} failed (may be non-existent articles or network errors). Refreshing articles list...`,
            { duration: 6000 }
          )
        } else {
          toast.success(`Successfully processed all ${actualSuccesses || successCount} articles! Refreshing articles list...`)
        }
      } else {
        const totalAttempted = urls.length
        toast.error(`Failed to process any of the ${totalAttempted} articles. Please check that the Wikipedia URLs exist and are valid.`, { duration: 6000 })
      }
    } catch (error) {
      setBulkProcessing(false)
      setBulkProgress({ 
        submitted: 0, 
        completed: 0, 
        total: 0, 
        currentUrl: '',
        processingArticles: new Map()
      })
      toast.error('Bulk processing failed')
      console.error('Bulk processing error:', error)
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

  const fetchRandomBulkArticles = async () => {
    if (randomArticleCount < 1 || randomArticleCount > 20) {
      toast.error('Please enter a number between 1 and 20')
      return
    }

    setIsLoadingRandomBulk(true)
    try {
      toast.loading(`Fetching ${randomArticleCount} random articles...`)
      
      const fetchPromises = Array.from({ length: randomArticleCount }, async () => {
        const response = await fetch('https://en.wikipedia.org/api/rest_v1/page/random/summary')
        if (!response.ok) {
          throw new Error('Failed to fetch random article')
        }
        const data = await response.json()
        return `https://en.wikipedia.org/wiki/${encodeURIComponent(data.title.replace(/ /g, '_'))}`
      })

      const randomUrls = await Promise.all(fetchPromises)
      
      // Replace existing bulk URLs
      const newUrls = randomUrls.join(', ')
      setBulkUrls(newUrls)
      
      toast.dismiss()
      toast.success(`Added ${randomArticleCount} random articles to bulk processing!`)
    } catch (error) {
      toast.dismiss()
      toast.error('Failed to fetch random articles')
      console.error('Random bulk articles fetch error:', error)
    } finally {
      setIsLoadingRandomBulk(false)
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
          queryClient.invalidateQueries({ queryKey: ['articles'] })
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
                  All Articles
                </h2>
                {articles.length > 0 && (
                  <div className="flex items-center space-x-4">
                    <span className="text-sm text-gray-400">
                      {articles.length} total • Page {currentPage} of {totalPages}
                    </span>
                    <button
                      onClick={handleSelectAll}
                      className="text-sm text-blue-400 hover:text-blue-300 font-medium"
                    >
                      {selectedArticles.length === articles.length ? 'Deselect All' : 'Select All'}
                    </button>
                  </div>
                )}
              </div>
              <div className="flex items-center space-x-3">
                <button
                  onClick={handleDownloadAllArticles}
                  disabled={selectedArticles.length === 0}
                  className="flex items-center space-x-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white text-sm font-medium rounded-lg transition-colors disabled:cursor-not-allowed focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-gray-800"
                  title={`Download ${selectedArticles.length} selected articles`}
                >
                  <ArrowDownTrayIcon className="h-4 w-4" />
                  <span>Download Selected ({selectedArticles.length})</span>
                </button>
                <button
                  onClick={handleDeleteSelectedArticles}
                  disabled={selectedArticles.length === 0}
                  className="flex items-center space-x-2 px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white text-sm font-medium rounded-lg transition-colors disabled:cursor-not-allowed focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:ring-offset-gray-800"
                  title={`Delete ${selectedArticles.length} selected articles`}
                >
                  <TrashIcon className="h-4 w-4" />
                  <span>Delete Selected ({selectedArticles.length})</span>
                </button>
              </div>
            </div>
            
            {articles.length === 0 ? (
              <div className="text-center py-16">
                <DocumentTextIcon className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400">
                  No articles processed yet. Add a Wikipedia URL to get started.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {currentArticles.map((article) => (
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
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            {/* Pagination */}
            {articles.length > 0 && totalPages > 1 && (
              <div className="mt-8 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <button
                    onClick={goToPrevPage}
                    disabled={currentPage === 1}
                    className="flex items-center space-x-1 px-3 py-2 text-sm font-medium text-gray-300 bg-gray-700 rounded-lg hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <ChevronLeftIcon className="h-4 w-4" />
                    <span>Previous</span>
                  </button>
                  
                  <div className="flex items-center space-x-1">
                    {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => {
                      const isCurrentPage = page === currentPage
                      const isNearCurrentPage = Math.abs(page - currentPage) <= 2
                      const isFirstOrLast = page === 1 || page === totalPages
                      
                      if (!isNearCurrentPage && !isFirstOrLast) {
                        if (page === currentPage - 3 || page === currentPage + 3) {
                          return (
                            <span key={page} className="px-2 text-gray-500">
                              ...
                            </span>
                          )
                        }
                        return null
                      }
                      
                      return (
                        <button
                          key={page}
                          onClick={() => goToPage(page)}
                          className={`px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                            isCurrentPage
                              ? 'bg-blue-600 text-white'
                              : 'text-gray-300 bg-gray-700 hover:bg-gray-600'
                          }`}
                        >
                          {page}
                        </button>
                      )
                    })}
                  </div>
                  
                  <button
                    onClick={goToNextPage}
                    disabled={currentPage === totalPages}
                    className="flex items-center space-x-1 px-3 py-2 text-sm font-medium text-gray-300 bg-gray-700 rounded-lg hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <span>Next</span>
                    <ChevronRightIcon className="h-4 w-4" />
                  </button>
                </div>
                
                <div className="text-sm text-gray-400">
                  Showing {startIndex + 1}-{Math.min(endIndex, articles.length)} of {articles.length} articles
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Bulk Processing Section */}
        <div className="bg-gray-800 rounded-2xl border border-gray-700 overflow-hidden">
          <div className="p-8">
            <h2 className="text-xl font-medium text-white mb-6">
              Bulk Process Articles
            </h2>
            
            <div className="space-y-6">
              {/* Random Articles Generator */}
              <div className="bg-gray-700 rounded-xl p-4">
                <h3 className="text-sm font-medium text-white mb-3">
                  Add Random Articles
                </h3>
                <div className="flex items-end space-x-3">
                  <div>
                    <label htmlFor="random-count" className="block text-xs font-medium text-gray-400 mb-2">
                      Number of articles (1-20)
                    </label>
                    <input
                      type="number"
                      id="random-count"
                      min="1"
                      max="20"
                      value={randomArticleCount}
                      onChange={(e) => setRandomArticleCount(parseInt(e.target.value) || 1)}
                      className="w-full px-3 py-2 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      disabled={isLoadingRandomBulk || bulkProcessing || isProcessing}
                    />
                  </div>
                  <button
                    onClick={fetchRandomBulkArticles}
                    disabled={isLoadingRandomBulk || bulkProcessing || isProcessing}
                    className="px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white text-sm font-medium rounded-lg transition-colors disabled:cursor-not-allowed focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-800 flex items-center space-x-2 h-15"
                  >
                    <ArrowPathIcon className={`h-4 w-4 ${isLoadingRandomBulk ? 'animate-spin' : ''}`} />
                    <span>{isLoadingRandomBulk ? 'Fetching...' : 'Add Random'}</span>
                  </button>
                </div>
              </div>

              <div>
                <label htmlFor="bulk-urls" className="block text-sm font-medium text-gray-300 mb-3">
                  Wikipedia URLs (separated by commas)
                </label>
                <textarea
                  id="bulk-urls"
                  rows={4}
                  value={bulkUrls}
                  onChange={(e) => setBulkUrls(e.target.value)}
                  placeholder="https://en.wikipedia.org/wiki/Machine_learning, https://en.wikipedia.org/wiki/Artificial_intelligence, https://en.wikipedia.org/wiki/Neural_network"
                  className="w-full px-4 py-3 rounded-xl border border-gray-600 bg-gray-700 text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  disabled={bulkProcessing || isProcessing}
                />
                <p className="mt-2 text-xs text-gray-400">
                  Enter multiple Wikipedia URLs separated by commas, or use the random article generator above. Uses the same settings as above.
                </p>
              </div>

                             {/* Bulk Processing Progress */}
               {bulkProcessing && (
                 <div className="bg-gray-700 rounded-xl p-4">
                   <div className="flex items-center justify-between mb-3">
                     <span className="text-sm font-medium text-white">
                       Processing Articles ({bulkProgress.completed}/{bulkProgress.total} completed)
                     </span>
                     <div className="flex items-center space-x-3">
                       <span className="text-xs text-gray-400">
                         {bulkProgress.total > 0 ? Math.round((bulkProgress.completed / bulkProgress.total) * 100) : 0}%
                       </span>
                       <button
                         onClick={handleStopBulkProcessing}
                         className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-xs font-medium rounded-lg transition-colors focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:ring-offset-gray-700"
                       >
                         Stop Processing
                       </button>
                     </div>
                   </div>
                   
                   {/* Submission Progress */}
                   <div className="mb-2">
                     <div className="flex justify-between text-xs text-gray-400 mb-1">
                       <span>Submitted: {bulkProgress.submitted}/{bulkProgress.total}</span>
                     </div>
                     <div className="w-full bg-gray-600 rounded-full h-1">
                       <div 
                         className="bg-yellow-500 h-1 rounded-full transition-all duration-300"
                         style={{ width: `${bulkProgress.total > 0 ? (bulkProgress.submitted / bulkProgress.total) * 100 : 0}%` }}
                       />
                     </div>
                   </div>
                   
                   {/* Completion Progress */}
                   <div className="mb-3">
                     <div className="flex justify-between text-xs text-gray-400 mb-1">
                       <span>Completed: {bulkProgress.completed}/{bulkProgress.total}</span>
                     </div>
                     <div className="w-full bg-gray-600 rounded-full h-2">
                       <div 
                         className="bg-green-500 h-2 rounded-full transition-all duration-300"
                         style={{ width: `${bulkProgress.total > 0 ? (bulkProgress.completed / bulkProgress.total) * 100 : 0}%` }}
                       />
                     </div>
                   </div>
                   
                   {bulkProgress.currentUrl && (
                     <p className="text-xs text-gray-400 truncate">
                       Status: {bulkProgress.currentUrl}
                     </p>
                   )}
                 </div>
               )}

                             <button
                 onClick={handleBulkProcessing}
                 disabled={bulkProcessing || isProcessing || !bulkUrls.trim()}
                 className="w-full py-3 px-6 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white font-medium rounded-xl transition-colors disabled:cursor-not-allowed focus:ring-2 focus:ring-green-500 focus:ring-offset-2 focus:ring-offset-gray-800"
               >
                 {bulkProcessing ? 
                   `Processing... (${bulkProgress.completed}/${bulkProgress.total} completed)` : 
                   'Process All Articles'
                 }
               </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomePage 