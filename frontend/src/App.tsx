import { useEffect, useState } from 'react'
import {
  Alert,
  Box,
  CircularProgress,
  Container,
  CssBaseline,
  Paper,
  ThemeProvider,
  Typography,
  createTheme,
} from '@mui/material'

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#1976d2' },
  },
})

type Health = {
  status: string
  chroma_collection: string
  document_count: number
}

function App() {
  const [health, setHealth] = useState<Health | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/health')
      .then((res) => {
        if (!res.ok) throw new Error(`API returned ${res.status}`)
        return res.json() as Promise<Health>
      })
      .then(setHealth)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="sm">
        <Box sx={{ py: 8 }}>
          <Typography variant="h3" component="h1" gutterBottom>
            Summarag
          </Typography>
          <Typography color="text.secondary" sx={{ mb: 2 }}>
            RAG stack: FastAPI, ChromaDB, React, and Material UI.
          </Typography>

          <Paper sx={{ p: 3, mt: 2 }}>
            {loading && (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                <CircularProgress size={32} />
              </Box>
            )}
            {error && <Alert severity="error">Backend unreachable: {error}</Alert>}
            {health && (
              <Alert severity="success">
                API is healthy. Chroma collection &quot;{health.chroma_collection}&quot; has{' '}
                {health.document_count} document(s).
              </Alert>
            )}
          </Paper>
        </Box>
      </Container>
    </ThemeProvider>
  )
}

export default App
