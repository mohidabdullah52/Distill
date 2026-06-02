import { useEffect, useState } from 'react'
import { fetchHealth, type HealthResponse } from '../api/health'

/** Poll backend health for LLM provider display in the header. */
export function useBackendHealth() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    const load = async () => {
      try {
        const data = await fetchHealth()
        if (!cancelled) setHealth(data)
      } catch {
        if (!cancelled) setHealth({ status: 'offline' })
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    load()
    const interval = setInterval(load, 30000)
    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [])

  return { health, loading }
}
