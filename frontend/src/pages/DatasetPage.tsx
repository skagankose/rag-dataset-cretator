import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import toast from 'react-hot-toast'
import { 
  DocumentTextIcon,
  MagnifyingGlassIcon,
  ClipboardDocumentIcon,
  ChevronLeftIcon,
  ChevronDownIcon,
  ChevronUpIcon,
} from '@heroicons/react/24/outline'

import { getDataset, getFileUrl, downloadFile, downloadDatasetJson, getChunks } from '../lib/api'

function DatasetPage() {
  const { articleId } = useParams<{ articleId: string }>()
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedQuestions, setExpandedQuestions] = useState<Set<number>>(new Set())

  const { data: dataset, isLoading } = useQuery({
    queryKey: ['dataset', articleId],
    queryFn: () => getDataset(articleId!),
    enabled: !!articleId,
  })

  const { data: chunks = [] } = useQuery({
    queryKey: ['chunks', articleId],
    queryFn: () => getChunks(articleId!),
    enabled: !!articleId,
  })

  // Create a map for quick chunk lookup
  const chunksMap = chunks.reduce((acc: Record<string, any>, chunk: any) => {
    acc[chunk.id] = chunk
    return acc
  }, {} as Record<string, any>)

  const filteredItems = dataset?.items.filter(item =>
    item.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.related_chunk_ids.some(id => id.toLowerCase().includes(searchQuery.toLowerCase()))
  ) || []

  const handleDownloadDataset = async () => {
    if (!articleId) return
    
    try {
      const blob = await downloadDatasetJson(articleId)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${dataset?.title?.replace(/[^a-zA-Z0-9_-]/g, '_').toLowerCase() || 'dataset'}_dataset.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      toast.success('Dataset downloaded as JSON!')
    } catch (error) {
      toast.error('Failed to download dataset')
    }
  }

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      toast.success('Copied to clipboard!')
    } catch (error) {
      toast.error('Failed to copy to clipboard')
    }
  }

  const toggleQuestionExpansion = (questionIndex: number) => {
    setExpandedQuestions((prev: Set<number>) => {
      const newSet = new Set(prev)
      if (newSet.has(questionIndex)) {
        newSet.delete(questionIndex)
      } else {
        newSet.add(questionIndex)
      }
      return newSet
    })
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-500 border-t-transparent mx-auto"></div>
          <p className="mt-4 text-gray-400">Loading dataset...</p>
        </div>
      </div>
    )
  }

  if (!dataset) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-white mb-4">
            Dataset not found
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
          <Link 
            to={`/articles/${articleId}`}
            className="text-gray-400 hover:text-gray-300 transition-colors"
          >
            {dataset.title}
          </Link>
          <span className="text-gray-600">/</span>
          <span className="text-white font-medium">
            Dataset
          </span>
        </nav>

        {/* Dataset Header */}
        <div className="bg-gray-800 rounded-2xl border border-gray-700 overflow-hidden">
          <div className="p-8">
            <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
              <div className="flex-1 min-w-0">
                <h1 className="text-3xl font-semibold text-white mb-4 leading-tight">
                  {dataset.title}
                </h1>
                <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-gray-400">
                  <span className="flex items-center">
                    <span className="font-medium">Total Questions:</span> 
                    <span className="ml-1">{dataset.total_questions}</span>
                  </span>
                  <span className="flex items-center">
                    <span className="font-medium">Created:</span> 
                    <span className="ml-1">{new Date(dataset.created_at).toLocaleDateString()}</span>
                  </span>
                </div>
              </div>
              
              <div className="flex flex-row lg:flex-col gap-3">
                <Link
                  to={`/articles/${articleId}`}
                  className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-xl text-white bg-blue-600 hover:bg-blue-700 transition-colors"
                >
                  <DocumentTextIcon className="h-4 w-4 mr-2" />
                  View Chunks
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Dataset Questions */}
        <div className="bg-gray-800 rounded-2xl border border-gray-700 overflow-hidden">
          <div className="p-8">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
              <h2 className="text-xl font-medium text-white">
                Questions ({dataset.total_questions})
              </h2>
              <button
                onClick={handleDownloadDataset}
                className="text-sm text-blue-400 hover:text-blue-300 font-medium self-start sm:self-auto"
              >
                Download Questions (JSON)
              </button>
            </div>

            {/* Search */}
            <div className="mb-6">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search questions..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-600 bg-gray-700 text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Questions List */}
            <div className="space-y-4">
              {filteredItems.map((item, index) => (
                <div key={index} className="border border-gray-600 rounded-xl overflow-hidden">
                  {/* Clickable question row */}
                  <div 
                    className="p-6 hover:bg-gray-700 transition-colors cursor-pointer"
                    onClick={() => toggleQuestionExpansion(index)}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-start space-x-4 flex-1 min-w-0">
                        <span className="inline-flex items-center justify-center h-8 w-8 rounded-full bg-blue-900 text-blue-200 text-sm font-medium flex-shrink-0">
                          {index + 1}
                        </span>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-white mb-3 leading-relaxed">
                            {item.question}
                          </p>
                          <div className="flex flex-wrap items-center gap-2">
                            <span className="text-xs text-gray-400 flex-shrink-0">
                              Related chunks:
                            </span>
                            {item.related_chunk_ids.map((chunkId) => (
                              <span
                                key={chunkId}
                                className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-600 text-gray-200"
                              >
                                {chunkId}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            copyToClipboard(item.question)
                          }}
                          className="flex-shrink-0 p-2 text-gray-400 hover:text-gray-200 hover:bg-gray-600 rounded-lg transition-colors"
                          title="Copy question"
                        >
                          <ClipboardDocumentIcon className="h-4 w-4" />
                        </button>
                        <div className="p-2">
                          {expandedQuestions.has(index) ? (
                            <ChevronUpIcon className="h-4 w-4 text-gray-400" />
                          ) : (
                            <ChevronDownIcon className="h-4 w-4 text-gray-400" />
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Expanded chunk content */}
                  {expandedQuestions.has(index) && (
                    <div className="border-t border-gray-600 p-6 bg-gray-800">
                      <div className="space-y-4">
                        {item.related_chunk_ids.map((chunkId) => {
                          const chunk = chunksMap[chunkId]
                          if (!chunk) return null
                          
                          return (
                            <div 
                              key={chunkId} 
                              className="bg-gray-700 border border-gray-600 rounded-lg p-4"
                            >
                              <div className="mb-2">
                                <div className="flex items-center gap-2">
                                  <span className="text-xs font-medium text-blue-300">
                                    Chunk: {chunkId}
                                  </span>
                                  {chunk.section && (
                                    <span className="text-xs text-gray-400">
                                      • {chunk.section}
                                    </span>
                                  )}
                                </div>
                              </div>
                              <div className="text-xs text-gray-300 leading-relaxed max-h-40 overflow-y-auto">
                                {chunk.content}
                              </div>
                              {chunk.heading_path && chunk.heading_path !== 'Lead' && (
                                <div className="mt-2 text-xs text-gray-500">
                                  Path: {chunk.heading_path}
                                </div>
                              )}
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  )}
                </div>
              ))}
              
              {filteredItems.length === 0 && searchQuery && (
                <div className="text-center py-12">
                  <MagnifyingGlassIcon className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400">
                    No questions found matching "{searchQuery}"
                  </p>
                </div>
              )}
              
              {filteredItems.length === 0 && !searchQuery && (
                <div className="text-center py-12">
                  <ClipboardDocumentIcon className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400">
                    No questions available in this dataset.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Dataset Format Info */}
        <div className="bg-blue-900/20 border border-blue-800 rounded-2xl p-6">
          <h3 className="text-sm font-medium text-blue-200 mb-3">
            Dataset Format
          </h3>
          <p className="text-sm text-blue-300 leading-relaxed">
            This dataset contains {dataset.total_questions} questions generated from the article chunks. 
            Each question is linked to specific chunk IDs that contain the relevant context. 
            The dataset can be downloaded as a JSON file with structured data for easy integration.
          </p>
        </div>
      </div>
    </div>
  )
}

export default DatasetPage 