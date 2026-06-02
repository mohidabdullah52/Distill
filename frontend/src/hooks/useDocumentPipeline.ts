import { useCallback, useReducer } from 'react'
import axios from 'axios'
import client from '../api/client'

export const STEPS = [
  'Upload Files',
  'Index Documents',
  'Generate Summary',
  'Download PDF',
] as const

type PipelineStatus =
  | 'idle'
  | 'uploading'
  | 'ingesting'
  | 'summarizing'
  | 'done'
  | 'error'

interface PipelineState {
  status: PipelineStatus
  activeStep: number
  files: File[]
  sessionId: string | null
  filesProcessed: string[]
  totalChunks: number
  downloadUrl: string | null
  pdfFilename: string | null
  summaryPreview: string | null
  error: string | null
}

type PipelineAction =
  | { type: 'SET_FILES'; payload: File[] }
  | { type: 'START_UPLOAD' }
  | {
      type: 'INGEST_SUCCESS'
      payload: {
        session_id: string
        files_processed: string[]
        total_chunks: number
      }
    }
  | { type: 'START_SUMMARIZE' }
  | {
      type: 'SUMMARIZE_SUCCESS'
      payload: {
        download_url: string
        pdf_filename: string
        summary_preview: string
      }
    }
  | { type: 'ERROR'; payload: string }
  | { type: 'RESET' }

const initialState: PipelineState = {
  status: 'idle',
  activeStep: 0,
  files: [],
  sessionId: null,
  filesProcessed: [],
  totalChunks: 0,
  downloadUrl: null,
  pdfFilename: null,
  summaryPreview: null,
  error: null,
}

/**
 * Updates pipeline state based on ingest and summarize progress events.
 *
 * @param {PipelineState} state - Current pipeline state.
 * @param {PipelineAction} action - Dispatched state transition.
 * @returns {PipelineState} Next pipeline state.
 */
function reducer(state: PipelineState, action: PipelineAction): PipelineState {
  switch (action.type) {
    case 'SET_FILES':
      return { ...state, files: action.payload, error: null }
    case 'START_UPLOAD':
      return { ...state, status: 'uploading', activeStep: 0, error: null }
    case 'INGEST_SUCCESS':
      return {
        ...state,
        status: 'ingesting',
        activeStep: 1,
        sessionId: action.payload.session_id,
        filesProcessed: action.payload.files_processed,
        totalChunks: action.payload.total_chunks,
      }
    case 'START_SUMMARIZE':
      return { ...state, status: 'summarizing', activeStep: 2 }
    case 'SUMMARIZE_SUCCESS':
      return {
        ...state,
        status: 'done',
        activeStep: 3,
        downloadUrl: action.payload.download_url,
        pdfFilename: action.payload.pdf_filename,
        summaryPreview: action.payload.summary_preview,
      }
    case 'ERROR':
      return { ...state, status: 'error', error: action.payload }
    case 'RESET':
      return { ...initialState }
    default:
      return state
  }
}

/**
 * Converts API error payloads into a user-facing message string.
 *
 * @param {unknown} detail - Error body from axios or the backend.
 * @returns {string} Readable error message for the UI.
 */
function formatError(detail: unknown): string {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((item) => JSON.stringify(item)).join('; ')
  }
  return 'An unexpected error occurred.'
}

/**
 * Manages upload, ingest, summarize, and result state for the document workflow.
 *
 * @returns {object} Pipeline state, step labels, and action handlers for the UI.
 */
export function useDocumentPipeline() {
  const [state, dispatch] = useReducer(reducer, initialState)

  const addFiles = useCallback((newFiles: FileList | File[]) => {
    dispatch({
      type: 'SET_FILES',
      payload: [...state.files, ...Array.from(newFiles)].slice(0, 10),
    })
  }, [state.files])

  const removeFile = useCallback((index: number) => {
    dispatch({
      type: 'SET_FILES',
      payload: state.files.filter((_, i) => i !== index),
    })
  }, [state.files])

  const run = useCallback(
    async (focusPrompt = '') => {
      if (state.files.length === 0) return

      dispatch({ type: 'START_UPLOAD' })

      const formData = new FormData()
      state.files.forEach((f) => formData.append('files', f))

      let ingestData: {
        session_id: string
        files_processed: string[]
        total_chunks: number
      }

      try {
        const res = await client.post('/ingest', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
        ingestData = res.data
        dispatch({ type: 'INGEST_SUCCESS', payload: ingestData })
        
        // Let the user see the "Index Documents" step is active before starting summarization
        await new Promise((resolve) => setTimeout(resolve, 1200))
      } catch (err: unknown) {
        const detail =
          axios.isAxiosError(err) && err.response?.data?.detail
            ? err.response.data.detail
            : 'Failed to ingest files.'
        dispatch({ type: 'ERROR', payload: formatError(detail) })
        return
      }

      dispatch({ type: 'START_SUMMARIZE' })
      try {
        const res = await client.post('/summarize', {
          session_id: ingestData.session_id,
          focus_prompt: focusPrompt || null,
        })
        dispatch({ type: 'SUMMARIZE_SUCCESS', payload: res.data })
      } catch (err: unknown) {
        const detail =
          axios.isAxiosError(err) && err.response?.data?.detail
            ? err.response.data.detail
            : 'Failed to generate summary.'
        dispatch({ type: 'ERROR', payload: formatError(detail) })
      }
    },
    [state.files],
  )

  const reset = useCallback(() => {
    if (state.sessionId) {
      client.post(`/cleanup/${state.sessionId}`).catch(() => {})
    }
    dispatch({ type: 'RESET' })
  }, [state.sessionId])

  const dismissError = useCallback(() => {
    if (state.sessionId) {
      client.post(`/cleanup/${state.sessionId}`).catch(() => {})
    }
    dispatch({ type: 'RESET' })
  }, [state.sessionId])

  return { state, STEPS, addFiles, removeFile, run, reset, dismissError }
}
