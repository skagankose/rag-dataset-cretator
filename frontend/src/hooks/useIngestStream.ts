import { useCallback, useEffect, useRef, useState } from 'react'
import type { IngestProgress } from '../types/api'

const API_BASE = 'http://localhost:8051'

interface UseIngestStreamResult {
  events: IngestProgress[]
  isConnected: boolean
  error: string | null
  lastEvent: IngestProgress | null
}

export function useIngestStream(runId: string | null): UseIngestStreamResult {
  const [events, setEvents] = useState<IngestProgress[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastEvent, setLastEvent] = useState<IngestProgress | null>(null)
  
  const eventSourceRef = useRef<EventSource | null>(null)

  const connect = useCallback(() => {
    if (!runId) return

    try {
      const eventSource = new EventSource(`${API_BASE}/ingest/stream/${runId}`)
      eventSourceRef.current = eventSource

      eventSource.onopen = () => {
        setIsConnected(true)
        setError(null)
      }

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          // Handle heartbeat
          if (data.type === 'heartbeat') {
            return
          }

          // Handle progress event
          const progressEvent = data as IngestProgress
          setEvents(prev => [...prev, progressEvent])
          setLastEvent(progressEvent)

          // Close connection on terminal events
          if (progressEvent.stage === 'DONE' || progressEvent.stage === 'FAILED') {
            eventSource.close()
            setIsConnected(false)
          }
        } catch (err) {
          console.error('Failed to parse SSE event:', err)
        }
      }

      eventSource.onerror = () => {
        setError('Connection lost')
        setIsConnected(false)
        eventSource.close()
      }
    } catch (err) {
      setError('Failed to connect')
      setIsConnected(false)
    }
  }, [runId])

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
      setIsConnected(false)
    }
  }, [])

  useEffect(() => {
    if (runId) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [runId, connect, disconnect])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect()
    }
  }, [disconnect])

  return {
    events,
    isConnected,
    error,
    lastEvent,
  }
} 