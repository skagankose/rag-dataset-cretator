import React, { useState, useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import JSZip from 'jszip'
import { 
  DocumentTextIcon,
  ArrowPathIcon,
  TrashIcon,
  RectangleStackIcon,
  ChatBubbleLeftRightIcon,
  ArrowDownTrayIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ArrowUpTrayIcon,
  DocumentPlusIcon,
  Cog6ToothIcon,
  GlobeAltIcon,
  FolderIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClipboardDocumentCheckIcon,
} from '@heroicons/react/24/outline'

import { startIngestion, getArticles, deleteArticle, downloadFile, getDataset, getChunks, uploadFiles, getConfig, validateArticle, exportArticle, exportAllArticles } from '../lib/api'
import type { IngestOptions } from '../types/api'

function HomePage() {
  const [bulkUrls, setBulkUrls] = useState('')
  const [randomArticleCount, setRandomArticleCount] = useState(5)
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
  
  // Validation state
  const [validationStatus, setValidationStatus] = useState<Record<string, 'correct' | 'incorrect' | 'validating' | null>>({})
  const [isValidating, setIsValidating] = useState(false)

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage] = useState(100)

  // File upload state
  const [files, setFiles] = useState<FileList | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [fileUploadProgress, setFileUploadProgress] = useState({ 
    submitted: 0, 
    completed: 0, 
    total: 0, 
    currentFile: '',
    processingFiles: new Map()
  })
  const [shouldStopFileUpload, setShouldStopFileUpload] = useState(false)

  const queryClient = useQueryClient()
  
  const { data: articles = [], refetch: refetchArticles } = useQuery({
    queryKey: ['articles'],
    queryFn: getArticles,
  })

  // Sync selectedArticles with available articles to remove stale IDs
  useEffect(() => {
    if (selectedArticles.length > 0) {
      const articleIds = new Set(articles.map(a => a.id))
      setSelectedArticles(prev => {
        const validSelection = prev.filter(id => articleIds.has(id))
        return validSelection.length === prev.length ? prev : validSelection
      })
    }
  }, [articles, selectedArticles.length]) // Only run when articles change or selection length changes to avoid loops

  // Fetch configuration to get prompt language for random articles
  const { data: config } = useQuery({
    queryKey: ['config'],
    queryFn: getConfig,
  })

  const promptLanguage = config?.prompt_language?.toLowerCase() || 'en'

  // Pagination logic
  const totalPages = Math.ceil(articles.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentArticles = articles.slice(startIndex, endIndex)

  // Optimize selection lookup
  const selectedSet = new Set(selectedArticles)

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

  const deleteMutation = useMutation({
    mutationFn: deleteArticle,
    onSuccess: () => {
      console.log('Article deleted successfully!')
      refetchArticles()
    },
    onError: (error) => {
      console.error(`Failed to delete article: ${error.message}`)
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
      console.log('Downloading article...')
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
      
      console.log('Article downloaded successfully!')
    } catch (error) {
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

  const handleSelectPage = () => {
    const currentPageIds = currentArticles.map(article => article.id)
    const allCurrentPageSelected = currentPageIds.every(id => selectedSet.has(id))
    
    if (allCurrentPageSelected) {
      // Deselect all articles on current page
      setSelectedArticles(prev => prev.filter(id => !currentPageIds.includes(id)))
    } else {
      // Select all articles on current page
      setSelectedArticles(prev => {
        const newSelection = [...prev]
        currentPageIds.forEach(id => {
          if (!newSelection.includes(id)) {
            newSelection.push(id)
          }
        })
        return newSelection
      })
    }
  }

  const handleSelectFailed = () => {
    // Find all articles with validation status 'incorrect'
    const failedArticleIds = articles
      .filter(article => validationStatus[article.id] === 'incorrect')
      .map(article => article.id)
    
    // Deselect everything and select only failed articles
    setSelectedArticles(failedArticleIds)
  }

  const handleDeleteSelectedArticles = async () => {
    if (selectedArticles.length === 0) {
      console.warn('No articles selected for deletion')
      return
    }

    const selectedTitles = articles
      .filter(article => selectedSet.has(article.id))
      .map(article => article.title)
      .join(', ')

    const confirmed = window.confirm(
      `Are you sure you want to delete ${selectedArticles.length} selected article(s)?\n\n${selectedTitles}\n\nThis will permanently remove the articles and all related files including chunks and datasets.`
    )
    
    if (!confirmed) return

    const totalArticles = selectedArticles.length
    let deletedCount = 0
    let failedCount = 0

    try {
      console.log(`Starting deletion of ${totalArticles} selected articles...`)
      
      // Process deletions in batches to avoid overwhelming the system
      const BATCH_SIZE = 5
      
      for (let i = 0; i < selectedArticles.length; i += BATCH_SIZE) {
        const batch = selectedArticles.slice(i, i + BATCH_SIZE)
        console.log(`Deleting batch ${Math.floor(i / BATCH_SIZE) + 1}/${Math.ceil(totalArticles / BATCH_SIZE)} (${batch.length} articles)...`)
        
        // Delete batch in parallel
        const batchPromises = batch.map(async (articleId) => {
          try {
            await deleteMutation.mutateAsync(articleId)
            deletedCount++
            return { success: true, articleId }
          } catch (error) {
            failedCount++
            console.error(`Failed to delete article ${articleId}:`, error)
            return { success: false, articleId, error }
          }
        })
        
        await Promise.all(batchPromises)
        
        // Short delay between batches to avoid overwhelming the system
        if (i + BATCH_SIZE < selectedArticles.length) {
          await new Promise(resolve => setTimeout(resolve, 100))
        }
      }
      
      // Clear selection after deletion
      setSelectedArticles([])
      
      console.log(`Deletion complete: ${deletedCount} succeeded, ${failedCount} failed out of ${totalArticles} total`)
      
      // Refetch articles to update the list
      refetchArticles()
    } catch (error) {
      console.error('Bulk delete error:', error)
      console.log(`Deleted ${deletedCount} articles before error occurred`)
      refetchArticles()
    }
  }

  const handleDeleteAllArticles = async () => {
    if (articles.length === 0) {
      console.warn('No articles to delete')
      return
    }

    const confirmed = window.confirm(
      `Are you sure you want to delete ALL ${articles.length} articles?\n\nThis will permanently remove all articles and related files including chunks and datasets.\n\nThis action cannot be undone!`
    )
    
    if (!confirmed) return

    const totalArticles = articles.length
    let deletedCount = 0
    let failedCount = 0

    try {
      console.log(`Starting deletion of ${totalArticles} articles...`)
      
      // Process deletions in batches to avoid overwhelming the system
      const BATCH_SIZE = 5
      const articleIds = articles.map(a => a.id)
      
      for (let i = 0; i < articleIds.length; i += BATCH_SIZE) {
        const batch = articleIds.slice(i, i + BATCH_SIZE)
        console.log(`Deleting batch ${Math.floor(i / BATCH_SIZE) + 1}/${Math.ceil(totalArticles / BATCH_SIZE)} (${batch.length} articles)...`)
        
        // Delete batch in parallel
        const batchPromises = batch.map(async (articleId) => {
          try {
            await deleteMutation.mutateAsync(articleId)
            deletedCount++
            return { success: true, articleId }
          } catch (error) {
            failedCount++
            console.error(`Failed to delete article ${articleId}:`, error)
            return { success: false, articleId, error }
          }
        })
        
        await Promise.all(batchPromises)
        
        // Short delay between batches to avoid overwhelming the system
        if (i + BATCH_SIZE < articleIds.length) {
          await new Promise(resolve => setTimeout(resolve, 100))
        }
      }
      
      // Clear selection after deletion
      setSelectedArticles([])
      
      console.log(`Deletion complete: ${deletedCount} succeeded, ${failedCount} failed out of ${totalArticles} total`)
      
      // Refetch articles to update the list
      refetchArticles()
    } catch (error) {
      console.error('Bulk delete all error:', error)
      console.log(`Deleted ${deletedCount} articles before error occurred`)
      refetchArticles()
    }
  }

  const handleValidateAllArticles = async () => {
    if (articles.length === 0) {
      console.warn('No articles to validate')
      return
    }

    setIsValidating(true)
    
    const totalArticles = articles.length
    let validatedCount = 0
    let correctCount = 0
    let incorrectCount = 0
    let errorCount = 0
    
    console.log(`Starting validation of ${totalArticles} article(s)...`)

    try {
      // Process validations in batches to avoid overwhelming the system
      const BATCH_SIZE = 3 // Smaller batch for validation as it's more intensive
      const articleList = [...articles]
      
      for (let i = 0; i < articleList.length; i += BATCH_SIZE) {
        const batch = articleList.slice(i, i + BATCH_SIZE)
        console.log(`Validating batch ${Math.floor(i / BATCH_SIZE) + 1}/${Math.ceil(totalArticles / BATCH_SIZE)} (${batch.length} articles)...`)
        
        // Set batch articles to validating state
        const validatingStatus: Record<string, 'validating'> = {}
        batch.forEach(article => {
          validatingStatus[article.id] = 'validating'
        })
        setValidationStatus(prev => ({ ...prev, ...validatingStatus }))
        
        // Validate batch in parallel
        const batchPromises = batch.map(async (article) => {
          try {
            const result = await validateArticle(article.id)
            validatedCount++
            if (result.is_correct) {
              correctCount++
            } else {
              incorrectCount++
            }
            return { 
              articleId: article.id, 
              isCorrect: result.is_correct,
              reason: result.reason,
              error: null
            }
          } catch (error) {
            validatedCount++
            errorCount++
            console.error(`Validation failed for article ${article.id}:`, error)
            return { 
              articleId: article.id, 
              isCorrect: false, 
              reason: '',
              error: error.message 
            }
          }
        })

        const batchResults = await Promise.all(batchPromises)
        
        // Update validation status for batch
        const batchStatus: Record<string, 'correct' | 'incorrect' | null> = {}
        batchResults.forEach(result => {
          if (result.error) {
            batchStatus[result.articleId] = null
          } else {
            batchStatus[result.articleId] = result.isCorrect ? 'correct' : 'incorrect'
          }
        })
        setValidationStatus(prev => ({ ...prev, ...batchStatus }))
        
        // Short delay between batches to avoid overwhelming the system
        if (i + BATCH_SIZE < articleList.length) {
          await new Promise(resolve => setTimeout(resolve, 200))
        }
      }
      
      // Log final results
      console.log(`Validation complete: ${correctCount} correct, ${incorrectCount} incorrect, ${errorCount} errors out of ${totalArticles} total`)
      
      if (errorCount > 0) {
        console.error(`Validation completed with errors: ${correctCount} correct, ${incorrectCount} incorrect, ${errorCount} failed`)
      } else if (incorrectCount > 0) {
        console.warn(`Validation completed: ${correctCount} correct, ${incorrectCount} incorrect`)
      } else {
        console.log(`All ${correctCount} article(s) validated successfully!`)
      }
    } catch (error) {
      console.error('Validation error:', error)
      console.log(`Validated ${validatedCount} articles before error occurred`)
    } finally {
      setIsValidating(false)
    }
  }

  const handleDownloadAllFromDatabase = async () => {
    if (articles.length === 0) {
      console.warn('No articles in the database to download')
      return
    }

    const confirmed = window.confirm(
      `Download all ${articles.length} articles from the database?\n\nThis will create a ZIP file with complete exports of every article including content, chunks, and questions.`
    )
    
    if (!confirmed) return

    try {
      console.log(`Downloading all ${articles.length} articles...`)
      
      // Call the backend endpoint that exports all articles as a ZIP
      const zipBlob = await exportAllArticles()
      
      // Create download link
      const url = window.URL.createObjectURL(zipBlob)
      const link = document.createElement('a')
      link.href = url
      
      // The filename will be set by the backend in Content-Disposition header
      // but we'll provide a default just in case
      const currentDate = new Date().toISOString().split('T')[0]
      link.download = `all_articles_export_${currentDate}.zip`
      
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      console.log(`Successfully downloaded all ${articles.length} articles!`)
    } catch (error) {
      console.error('Download all error:', error)
    }
  }

  const handleValidateSelectedArticles = async () => {
    if (selectedArticles.length === 0) {
      console.warn('No articles selected for validation')
      return
    }

    setIsValidating(true)
    
    const totalArticles = selectedArticles.length
    let validatedCount = 0
    let correctCount = 0
    let incorrectCount = 0
    let errorCount = 0
    
    console.log(`Starting validation of ${totalArticles} selected article(s)...`)

    try {
      // Process validations in batches to avoid overwhelming the system
      const BATCH_SIZE = 3 // Smaller batch for validation as it's more intensive
      
      for (let i = 0; i < selectedArticles.length; i += BATCH_SIZE) {
        const batch = selectedArticles.slice(i, i + BATCH_SIZE)
        console.log(`Validating batch ${Math.floor(i / BATCH_SIZE) + 1}/${Math.ceil(totalArticles / BATCH_SIZE)} (${batch.length} articles)...`)
        
        // Set batch articles to validating state
        const validatingStatus: Record<string, 'validating'> = {}
        batch.forEach(articleId => {
          validatingStatus[articleId] = 'validating'
        })
        setValidationStatus(prev => ({ ...prev, ...validatingStatus }))
        
        // Validate batch in parallel
        const batchPromises = batch.map(async (articleId) => {
          try {
            const result = await validateArticle(articleId)
            validatedCount++
            if (result.is_correct) {
              correctCount++
            } else {
              incorrectCount++
            }
            return { 
              articleId, 
              result,
              error: null
            }
          } catch (error) {
            validatedCount++
            errorCount++
            console.error(`Failed to validate article ${articleId}:`, error)
            return { 
              articleId, 
              result: null, 
              error
            }
          }
        })

        const batchResults = await Promise.all(batchPromises)
        
        // Update validation status for batch
        const batchStatus: Record<string, 'correct' | 'incorrect' | null> = {}
        batchResults.forEach(result => {
          if (result.error || !result.result) {
            batchStatus[result.articleId] = null
          } else {
            batchStatus[result.articleId] = result.result.is_correct ? 'correct' : 'incorrect'
          }
        })
        setValidationStatus(prev => ({ ...prev, ...batchStatus }))
        
        // Short delay between batches to avoid overwhelming the system
        if (i + BATCH_SIZE < selectedArticles.length) {
          await new Promise(resolve => setTimeout(resolve, 200))
        }
      }
      
      // Log final results
      console.log(`Validation complete: ${correctCount} correct, ${incorrectCount} incorrect, ${errorCount} errors out of ${totalArticles} total`)
      
      if (errorCount > 0) {
        console.error(`Validation completed with errors: ${correctCount} correct, ${incorrectCount} incorrect, ${errorCount} failed`)
      } else if (incorrectCount > 0) {
        console.warn(`Validation completed: ${correctCount} correct, ${incorrectCount} incorrect`)
      } else {
        console.log(`All ${correctCount} article(s) validated successfully!`)
      }
    } catch (error) {
      console.error('Validation error:', error)
      console.log(`Validated ${validatedCount} articles before error occurred`)
    } finally {
      setIsValidating(false)
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
      console.warn('Bulk processing is already in progress')
      return
    }

    if (!bulkUrls.trim()) {
      console.warn('Please enter Wikipedia URLs')
      return
    }

    // Parse URLs from comma-separated input
    const urls = bulkUrls
      .split(',')
      .map(url => url.trim())
      .filter(url => url.length > 0)

    if (urls.length === 0) {
      console.warn('Please enter valid Wikipedia URLs')
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
      console.error(`Invalid Wikipedia URL found: "${firstInvalid}". Please ensure all URLs are valid Wikipedia links.`)
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
          console.info('Bulk processing stopped by user')
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
          console.log(`Bulk processing completed! ${actualSuccesses || successCount} articles processed successfully. ${totalErrors} failed (may be non-existent articles or network errors). Refreshing articles list...`)
        } else {
          console.log(`Successfully processed all ${actualSuccesses || successCount} articles! Refreshing articles list...`)
        }
      } else {
        const totalAttempted = urls.length
        console.error(`Failed to process any of the ${totalAttempted} articles. Please check that the Wikipedia URLs exist and are valid.`)
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
      console.error('Bulk processing error:', error)
    }
  }

  const fetchRandomBulkArticles = async () => {
    if (randomArticleCount < 1 || randomArticleCount > 1000) {
      console.warn('Please enter a number between 1 and 1000')
      return
    }

    setIsLoadingRandomBulk(true)
    try {
      console.log(`Fetching ${randomArticleCount} random articles...`)
      
      // Use Wikipedia's random page API with appropriate language
      const lang = promptLanguage === 'tr' ? 'tr' : 'en'
      
      const fetchPromises = Array.from({ length: randomArticleCount }, async () => {
        const response = await fetch(`https://${lang}.wikipedia.org/api/rest_v1/page/random/summary`)
        if (!response.ok) {
          throw new Error('Failed to fetch random article')
        }
        const data = await response.json()
        return `https://${lang}.wikipedia.org/wiki/${encodeURIComponent(data.title.replace(/ /g, '_'))}`
      })

      const randomUrls = await Promise.all(fetchPromises)
      
      // Replace existing bulk URLs
      const newUrls = randomUrls.join(', ')
      setBulkUrls(newUrls)
      
      console.log(`Added ${randomArticleCount} random articles to bulk processing!`)
    } catch (error) {
      console.error('Random bulk articles fetch error:', error)
    } finally {
      setIsLoadingRandomBulk(false)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFiles(e.target.files)
    }
  }

  const handleStopFileUpload = () => {
    setShouldStopFileUpload(true)
    setIsUploading(false)
    setFileUploadProgress({ 
      submitted: 0, 
      completed: 0, 
      total: 0, 
      currentFile: '',
      processingFiles: new Map()
    })
    setShouldStopFileUpload(false)
    
    // Refresh the page to ensure clean state
    window.location.reload()
  }

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!files || files.length === 0) {
      console.warn('Please select files to upload')
      return
    }

    if (isUploading) {
      console.warn('File upload is already in progress')
      return
    }

    setIsUploading(true)
    setShouldStopFileUpload(false)
      const fileList = Array.from(files)
    setFileUploadProgress({ 
      submitted: 0, 
      completed: 0, 
      total: fileList.length, 
      currentFile: '',
      processingFiles: new Map()
    })

    try {
      let successCount = 0
      let errorCount = 0
      const processingFiles = new Map()

      // Step 1: Submit all files for processing
      for (let i = 0; i < fileList.length; i++) {
        // Check if user wants to stop processing
        if (shouldStopFileUpload) {
          console.info('File upload stopped by user')
          break
        }

        const currentFile = fileList[i]
        setFileUploadProgress(prev => ({ 
          ...prev, 
          submitted: i + 1, 
          currentFile: `Uploading: ${currentFile.name}` 
        }))

        try {
          const responses = await uploadFiles([currentFile], options)
          
          if (responses.length > 0 && responses[0].status === 'started') {
            processingFiles.set(responses[0].run_id, {
              fileName: currentFile.name,
              status: 'processing',
              runId: responses[0].run_id,
              startTime: Date.now()
            })
            successCount++
          } else if (responses[0].status === 'existing') {
            successCount++
            setFileUploadProgress(prev => ({ 
              ...prev, 
              completed: prev.completed + 1 
            }))
          }
        } catch (error) {
          console.error(`Failed to upload ${currentFile.name}:`, error)
          errorCount++
          setFileUploadProgress(prev => ({ 
            ...prev, 
            completed: prev.completed + 1,
            currentFile: `Failed: ${currentFile.name}`
          }))
        }

        // Small delay between uploads
        if (i < fileList.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 300))
        }
      }

      // Step 2: Monitor processing completion
      const monitorCompletion = () => {
        return new Promise((resolve) => {
          const startTime = Date.now()
          const maxTimeout = 300000 // 5 minutes total timeout
          const fileTimeout = 60000 // 1 minute per file timeout

          const checkInterval = setInterval(async () => {
            // Check if user wants to stop processing
            if (shouldStopFileUpload) {
              clearInterval(checkInterval)
              resolve(null)
              return
            }

            const activeProcessing = Array.from(processingFiles.values())
              .filter(file => file.status === 'processing')

            if (activeProcessing.length === 0) {
              clearInterval(checkInterval)
              resolve(null)
              return
            }

            // Check for files that have been processing too long
            const now = Date.now()
            let timedOutFiles = 0

            processingFiles.forEach((file, runId) => {
              if (file.status === 'processing') {
                const processingTime = now - (file.startTime || now)
                
                if (processingTime > fileTimeout) {
                  console.warn(`File timed out after ${processingTime}ms: ${file.fileName}`)
                  file.status = 'failed'
                  file.error = 'Processing timeout'
                  timedOutFiles++
                  errorCount++
                }
              }
            })

            // Check articles list to see if new articles have appeared
            try {
              const currentArticles = await getArticles()
              let newCompletions = 0

              processingFiles.forEach((file, runId) => {
                if (file.status === 'processing') {
                  // Check if this file now exists in the articles list
                  // Match filename with article title (removing extension and normalizing separators)
                  // Backend logic: filename without extension, replace _/- with space, clean whitespace
                  const normalizedFileName = file.fileName.replace(/\.md$/i, '')
                    .replace(/[_-]/g, ' ')
                    .replace(/\s+/g, ' ')
                    .trim()
                    .toLowerCase()

                  const found = currentArticles.some(a => 
                    a.title.toLowerCase().includes(normalizedFileName)
                  )
                  
                  if (found) {
                    file.status = 'completed'
                    newCompletions++
                  }
                }
              })

              const totalNewCompletions = newCompletions + timedOutFiles
              if (totalNewCompletions > 0) {
                setFileUploadProgress(prev => ({ 
                  ...prev, 
                  completed: prev.completed + totalNewCompletions,
                  currentFile: `Completed ${prev.completed + totalNewCompletions}/${prev.total} files${timedOutFiles > 0 ? ` (${timedOutFiles} failed)` : ''}`
                }))
              }
            } catch (error) {
              console.error('Error checking file completion:', error)
            }

            // Global timeout
            if (now - startTime > maxTimeout) {
              console.warn('Global timeout reached, stopping file upload monitor')
              
              let remainingFiles = 0
              processingFiles.forEach((file, runId) => {
                if (file.status === 'processing') {
                  file.status = 'failed'
                  file.error = 'Global timeout reached'
                  remainingFiles++
                  errorCount++
                }
              })

              if (remainingFiles > 0) {
                setFileUploadProgress(prev => ({ 
                  ...prev, 
                  completed: prev.completed + remainingFiles,
                  currentFile: `Timeout reached - marked ${remainingFiles} remaining files as failed`
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
      if (processingFiles.size > 0) {
        setFileUploadProgress(prev => ({ 
          ...prev, 
          currentFile: `Waiting for ${processingFiles.size} files to complete processing...` 
        }))
        await monitorCompletion()
      }

      setIsUploading(false)
      setFileUploadProgress({ 
        submitted: 0, 
        completed: 0, 
        total: 0, 
        currentFile: '',
        processingFiles: new Map()
      })
      
      // Reset file input
      const fileInput = document.getElementById('file-upload') as HTMLInputElement
      if (fileInput) fileInput.value = ''
      setFiles(null)

      // Count final results
      const actualSuccesses = Array.from(processingFiles.values())
        .filter(file => file.status === 'completed').length
      const actualFailures = Array.from(processingFiles.values())
        .filter(file => file.status === 'failed').length

      if (successCount > 0 || actualSuccesses > 0) {
        // Invalidate and refetch articles
        queryClient.invalidateQueries({ queryKey: ['articles'] })
        
        const pollForUpdates = async (attempts = 0) => {
          if (attempts < 10) {
            await new Promise(resolve => setTimeout(resolve, 2000))
            await refetchArticles()
            setTimeout(() => pollForUpdates(attempts + 1), 2000)
          }
        }
        
        pollForUpdates()
        
        const totalErrors = errorCount + actualFailures
        if (totalErrors > 0) {
          console.log(`File upload completed! ${actualSuccesses || successCount} files processed successfully. ${totalErrors} failed.`)
        } else {
          console.log(`Successfully processed all ${actualSuccesses || successCount} files!`)
        }
      } else {
        console.error(`Failed to upload all ${fileList.length} files.`)
      }
    } catch (error) {
      setIsUploading(false)
      setFileUploadProgress({ 
        submitted: 0, 
        completed: 0, 
        total: 0, 
        currentFile: '',
        processingFiles: new Map()
      })
      console.error('File upload error:', error)
    }
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-5xl mx-auto px-6 py-12 space-y-12">

        {/* Processing Settings */}
        <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
          <div className="p-8">
            <div className="flex items-center space-x-3 mb-6">
              <Cog6ToothIcon className="h-6 w-6 text-gray-900" />
              <h2 className="text-xl font-medium text-black">
                Processing Settings
              </h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Chunk Size
                </label>
                <input
                  type="number"
                  min="100"
                  max="5000"
                  value={options.chunk_size}
                  onChange={(e) => setOptions(prev => ({ ...prev, chunk_size: parseInt(e.target.value) }))}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 bg-white text-black focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                  disabled={isUploading || bulkProcessing}
                />
                <p className="mt-1 text-xs text-gray-500">
                  Characters per chunk (100-5000)
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Total Questions
                </label>
                <input
                  type="number"
                  min="1"
                  max="50"
                  value={options.total_questions}
                  onChange={(e) => setOptions(prev => ({ ...prev, total_questions: parseInt(e.target.value) }))}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 bg-white text-black focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                  disabled={isUploading || bulkProcessing}
                />
                <p className="mt-1 text-xs text-gray-500">
                  Questions to generate (1-50)
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Split Strategy
                </label>
                <select
                  value={options.split_strategy}
                  onChange={(e) => setOptions(prev => ({ ...prev, split_strategy: e.target.value as 'recursive' | 'header_aware' }))}
                  className="w-full h-10 px-3 py-2 rounded-lg border border-gray-300 bg-white text-black focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                  disabled={isUploading || bulkProcessing}
                >
                  <option value="recursive">Recursive</option>
                  <option value="header_aware">Header Aware</option>
                </select>
                <p className="mt-1 text-xs text-gray-500">
                  How to split the text
                </p>
              </div>
            </div>
          </div>
        </div>

                {/* File Upload Section */}
                <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
          <div className="p-8">
            <div className="flex items-center space-x-3 mb-6">
              <DocumentPlusIcon className="h-6 w-6 text-gray-900" />
              <h2 className="text-xl font-medium text-black">
                Upload Markdown Files
              </h2>
            </div>
            
            <form onSubmit={handleFileUpload} className="space-y-6">
              <div className="flex items-center justify-center w-full">
                <label htmlFor="file-upload" className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-xl cursor-pointer bg-gray-50 hover:bg-gray-100 hover:border-gray-900 transition-colors">
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <ArrowUpTrayIcon className="w-8 h-8 mb-3 text-gray-400" />
                    <p className="mb-2 text-sm text-gray-600">
                      <span className="font-semibold text-black">Click to upload</span>
                    </p>
                    <p className="text-xs text-gray-500">
                      Markdown files (.md)
                    </p>
                  </div>
                  <input 
                    id="file-upload" 
                    type="file" 
                    className="hidden" 
                    multiple 
                    accept=".md,.markdown"
                    onChange={handleFileChange}
                    disabled={isUploading || bulkProcessing}
                  />
                </label>
              </div>

              {files && files.length > 0 && (
                <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">
                      Selected {files.length} file(s):
                    </span>
                    <button 
                      type="button"
                      onClick={() => {
                        setFiles(null)
                        const fileInput = document.getElementById('file-upload') as HTMLInputElement
                        if (fileInput) fileInput.value = ''
                      }}
                      className="text-xs text-gray-900 hover:text-gray-700 font-medium"
                    >
                      Clear
                    </button>
                  </div>
                  <ul className="mt-2 space-y-1 max-h-32 overflow-y-auto">
                    {(Array.from(files) as File[]).map((file, index) => (
                      <li key={index} className="text-xs text-gray-600 truncate pl-2 border-l-2 border-gray-400">
                        {file.name} <span className="opacity-50">({file.size} bytes)</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* File Upload Processing */}
              {isUploading && (
                <div className="bg-gray-100 rounded-xl p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <ArrowPathIcon className="h-5 w-5 text-gray-900 animate-spin" />
                      <span className="text-sm font-medium text-black">
                        Processing files...
                      </span>
                    </div>
                    <button
                      onClick={handleStopFileUpload}
                      className="px-3 py-1 bg-gray-900 hover:bg-gray-700 text-white text-xs font-medium rounded-lg transition-colors focus:ring-2 focus:ring-gray-900 focus:ring-offset-2 focus:ring-offset-white"
                    >
                      STOP
                    </button>
                  </div>
                </div>
              )}

              <button
                type="submit"
                disabled={isUploading || !files || files.length === 0 || bulkProcessing}
                className="w-full py-3 px-6 bg-gray-900 hover:bg-gray-700 disabled:bg-gray-300 text-white font-medium rounded-xl transition-colors disabled:cursor-not-allowed focus:ring-2 focus:ring-gray-900 focus:ring-offset-2 focus:ring-offset-white"
              >
                {isUploading ? 'Processing...' : 'Upload and Process Files'}
              </button>
            </form>
          </div>
        </div>

        {/* Bulk Processing Section */}
        <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
          <div className="p-8">
            <div className="flex items-center space-x-3 mb-6">
              <GlobeAltIcon className="h-6 w-6 text-gray-900" />
              <h2 className="text-xl font-medium text-black">
                Process Wikipedia Articles
              </h2>
            </div>
            
            <div className="space-y-6">
              {/* Random Articles Generator */}
              <div className="bg-gray-100 rounded-xl p-4">
                <h3 className="text-sm font-medium text-black mb-3">
                  Add Random Articles
                </h3>
                <div className="flex items-end space-x-3">
                  <div>
                    <label htmlFor="random-count" className="block text-xs font-medium text-gray-600 mb-2">
                      Number of articles (1-1000)
                    </label>
                    <input
                      type="number"
                      id="random-count"
                      min="1"
                      max="1000"
                      value={randomArticleCount}
                      onChange={(e) => setRandomArticleCount(parseInt(e.target.value) || 1)}
                      className="w-full px-3 py-2 rounded-lg border border-gray-300 bg-white text-black focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                      disabled={isLoadingRandomBulk || bulkProcessing || isUploading}
                    />
                  </div>
                  <button
                    onClick={fetchRandomBulkArticles}
                    disabled={isLoadingRandomBulk || bulkProcessing || isUploading}
                    className="px-4 py-3 bg-black hover:bg-gray-800 disabled:bg-gray-300 text-white text-sm font-medium rounded-lg transition-colors disabled:cursor-not-allowed focus:ring-2 focus:ring-gray-900 focus:ring-offset-2 focus:ring-offset-white flex items-center space-x-2 h-15"
                  >
                    <ArrowPathIcon className={`h-4 w-4 ${isLoadingRandomBulk ? 'animate-spin' : ''}`} />
                    <span>{isLoadingRandomBulk ? 'Fetching...' : 'Add Random'}</span>
                  </button>
                </div>
              </div>

              <div>
                <label htmlFor="bulk-urls" className="block text-sm font-medium text-gray-700 mb-3">
                  Wikipedia URLs (separated by commas)
                </label>
                <textarea
                  id="bulk-urls"
                  rows={4}
                  value={bulkUrls}
                  onChange={(e) => setBulkUrls(e.target.value)}
                  placeholder="https://en.wikipedia.org/wiki/Machine_learning, https://en.wikipedia.org/wiki/Artificial_intelligence, https://en.wikipedia.org/wiki/Neural_network"
                  className="w-full px-4 py-3 rounded-xl border border-gray-300 bg-white text-black placeholder-gray-400 focus:ring-2 focus:ring-gray-900 focus:border-transparent resize-none"
                  disabled={bulkProcessing || isUploading}
                />
              </div>

              {/* Bulk Processing */}
              {bulkProcessing && (
                <div className="bg-gray-100 rounded-xl p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <ArrowPathIcon className="h-5 w-5 text-gray-900 animate-spin" />
                      <span className="text-sm font-medium text-black">
                        Processing articles...
                      </span>
                    </div>
                    <button
                      onClick={handleStopBulkProcessing}
                      className="px-3 py-1 bg-gray-900 hover:bg-gray-700 text-white text-xs font-medium rounded-lg transition-colors focus:ring-2 focus:ring-gray-900 focus:ring-offset-2 focus:ring-offset-white"
                    >
                      STOP
                    </button>
                  </div>
                </div>
              )}

              <button
                onClick={handleBulkProcessing}
                disabled={bulkProcessing || isUploading || !bulkUrls.trim()}
                className="w-full py-3 px-6 bg-gray-900 hover:bg-gray-700 disabled:bg-gray-300 text-white font-medium rounded-xl transition-colors disabled:cursor-not-allowed focus:ring-2 focus:ring-gray-900 focus:ring-offset-2 focus:ring-offset-white"
              >
                {bulkProcessing ? 'Processing...' : 'Process All Articles'}
              </button>
            </div>
          </div>
        </div>

        {/* Articles List */}
        <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
          <div className="p-8">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <FolderIcon className="h-6 w-6 text-gray-900" />
                <h2 className="text-xl font-medium text-black">
                  All Articles
                </h2>
              </div>
              <div className="flex items-center space-x-3">
                <button
                  onClick={handleDownloadAllFromDatabase}
                  disabled={articles.length === 0}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-200 text-white disabled:text-gray-400 text-sm font-medium rounded-lg transition-colors disabled:cursor-not-allowed focus:ring-2 focus:ring-blue-600 focus:ring-offset-2 focus:ring-offset-white"
                  title={`Download all ${articles.length} articles from database`}
                >
                  <ArrowDownTrayIcon className="h-4 w-4" />
                  <span>Download ({articles.length})</span>
                </button>
                <button
                  onClick={handleValidateAllArticles}
                  disabled={articles.length === 0 || isValidating}
                  className="flex items-center space-x-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-200 text-white disabled:text-gray-400 text-sm font-medium rounded-lg transition-colors disabled:cursor-not-allowed focus:ring-2 focus:ring-gray-900 focus:ring-offset-2 focus:ring-offset-white"
                  title={`Validate all ${articles.length} articles`}
                >
                  <ClipboardDocumentCheckIcon className="h-4 w-4" />
                  <span>{isValidating ? 'Validating...' : `Validate (${articles.length})`}</span>
                </button>
                <button
                  onClick={handleDeleteAllArticles}
                  disabled={articles.length === 0}
                  className="flex items-center space-x-2 px-4 py-2 bg-red-600 hover:bg-red-500 disabled:bg-gray-200 text-white disabled:text-gray-400 text-sm font-medium rounded-lg transition-colors disabled:cursor-not-allowed focus:ring-2 focus:ring-red-600 focus:ring-offset-2 focus:ring-offset-white"
                  title={`Delete all ${articles.length} articles`}
                >
                  <TrashIcon className="h-4 w-4" />
                  <span>Delete ({articles.length})</span>
                </button>
              </div>
            </div>
            
            {articles.length > 0 && (
              <div className="flex items-center justify-between mb-6 pt-4 border-t border-gray-200">
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-600">
                    {articles.length} total • Page {currentPage} of {totalPages}
                  </span>
                  <button
                    onClick={handleSelectPage}
                    className="text-sm text-gray-900 hover:text-gray-700 font-medium"
                  >
                    {currentArticles.every(article => selectedSet.has(article.id)) && currentArticles.length > 0
                      ? 'Deselect Page' 
                      : 'Select Page'}
                  </button>
                  <button
                    onClick={handleSelectFailed}
                    disabled={!articles.some(article => validationStatus[article.id] === 'incorrect')}
                    className="text-sm text-red-600 hover:text-red-700 font-medium disabled:text-gray-400 disabled:cursor-not-allowed"
                    title="Select only failed articles"
                  >
                    Select Failed
                  </button>
                </div>
                <div className="flex items-center space-x-3">
                  <button
                    onClick={handleValidateSelectedArticles}
                    disabled={selectedArticles.length === 0 || isValidating}
                    className="flex items-center space-x-2 px-3 py-2 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-200 text-white disabled:text-gray-400 text-sm font-medium rounded-lg transition-colors disabled:cursor-not-allowed focus:ring-2 focus:ring-gray-900 focus:ring-offset-2 focus:ring-offset-white"
                    title={`Validate ${selectedArticles.length} selected articles`}
                  >
                    <ClipboardDocumentCheckIcon className="h-4 w-4" />
                    <span>Validate ({selectedArticles.length})</span>
                  </button>
                  <button
                    onClick={handleDeleteSelectedArticles}
                    disabled={selectedArticles.length === 0}
                    className="flex items-center space-x-2 px-3 py-2 bg-gray-900 hover:bg-gray-700 disabled:bg-gray-200 text-white disabled:text-gray-400 text-sm font-medium rounded-lg transition-colors disabled:cursor-not-allowed focus:ring-2 focus:ring-gray-900 focus:ring-offset-2 focus:ring-offset-white"
                    title={`Delete ${selectedArticles.length} selected articles`}
                  >
                    <TrashIcon className="h-4 w-4" />
                    <span>Delete ({selectedArticles.length})</span>
                  </button>
                </div>
              </div>
            )}
            
            {articles.length === 0 ? (
              <div className="text-center py-16">
                <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">
                  No articles processed yet.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {currentArticles.map((article) => (
                  <div 
                    key={article.id} 
                    onClick={() => handleArticleSelection(article.id)}
                    className={`group flex items-center justify-between p-4 rounded-xl border transition-colors cursor-pointer ${
                      selectedSet.has(article.id) 
                        ? 'border-gray-900 bg-gray-50' 
                        : 'border-gray-200 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center space-x-4 min-w-0 flex-1">
                      <div className="flex-shrink-0">
                        <input
                          type="checkbox"
                          checked={selectedSet.has(article.id)}
                          onChange={(e) => {
                            e.stopPropagation()
                            handleArticleSelection(article.id)
                          }}
                          onClick={(e) => e.stopPropagation()}
                          className="h-4 w-4 rounded border-gray-300 bg-white text-gray-900 focus:ring-gray-900 focus:ring-offset-0"
                        />
                      </div>
                      <div className="flex-shrink-0">
                        <DocumentTextIcon className="h-5 w-5 text-gray-600" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center space-x-2">
                          <h3 className="text-sm font-medium text-black truncate">
                            {article.title}
                          </h3>
                          {validationStatus[article.id] === 'validating' && (
                            <ArrowPathIcon className="h-4 w-4 text-blue-500 animate-spin flex-shrink-0" />
                          )}
                          {validationStatus[article.id] === 'correct' && (
                            <CheckCircleIcon className="h-5 w-5 text-green-500 flex-shrink-0" title="Validation passed" />
                          )}
                          {validationStatus[article.id] === 'incorrect' && (
                            <XCircleIcon className="h-5 w-5 text-red-500 flex-shrink-0" title="Validation failed" />
                          )}
                        </div>
                        <p className="text-xs text-gray-600 mt-1">
                          {article.lang} • {new Date(article.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3 opacity-70 group-hover:opacity-100 transition-opacity">
                      <Link
                        to={`/articles/${article.id}`}
                        onClick={(e) => e.stopPropagation()}
                        className="text-sm text-gray-700 hover:text-black flex items-center space-x-1 font-medium"
                      >
                        <RectangleStackIcon className="h-4 w-4" />
                        <span>Chunks</span>
                      </Link>
                      <Link
                        to={`/dataset/${article.id}`}
                        onClick={(e) => e.stopPropagation()}
                        className="text-sm text-gray-700 hover:text-black flex items-center space-x-1 font-medium"
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
                    className="flex items-center space-x-1 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
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
                            <span key={page} className="px-2 text-gray-400">
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
                              ? 'bg-black text-white'
                              : 'text-gray-700 bg-gray-100 hover:bg-gray-200'
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
                    className="flex items-center space-x-1 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <span>Next</span>
                    <ChevronRightIcon className="h-4 w-4" />
                  </button>
                </div>
                
                <div className="text-sm text-gray-600">
                  Showing {startIndex + 1}-{Math.min(endIndex, articles.length)} of {articles.length} articles
                </div>
              </div>
            )}
          </div>
        </div>
        {/* Download Dataset Section */}
      </div>
    </div>
  )
}

export default HomePage 