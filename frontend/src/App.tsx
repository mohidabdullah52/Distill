import { useState } from 'react'
import {
  Box,
  Button,
  Container,
  CssBaseline,
  Divider,
  Paper,
  TextField,
  ThemeProvider,
  Typography,
} from '@mui/material'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import theme from './theme'
import DropZone from './components/DropZone'
import FileList from './components/FileList'
import ProcessingStatus from './components/ProcessingStatus'
import ResultCard from './components/ResultCard'
import ErrorAlert from './components/ErrorAlert'
import { useDocumentPipeline } from './hooks/useDocumentPipeline'

export default function App() {
  const { state, STEPS, addFiles, removeFile, run, reset, dismissError } =
    useDocumentPipeline()
  const [focusPrompt, setFocusPrompt] = useState('')

  const isProcessing = ['uploading', 'ingesting', 'summarizing'].includes(
    state.status,
  )
  const isDone = state.status === 'done'

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: '100vh',
          bgcolor: 'background.default',
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'center',
          pt: 6,
          pb: 8,
        }}
      >
        <Container maxWidth="sm">
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 1,
                mb: 1,
              }}
            >
              <AutoAwesomeIcon color="primary" sx={{ fontSize: 32 }} />
              <Typography variant="h4" color="primary.dark">
                Distill
              </Typography>
            </Box>
            <Typography variant="body1" color="text.secondary">
              Upload PDFs or PowerPoints — get a compact, AI-generated summary PDF
            </Typography>
          </Box>

          <Paper elevation={1} sx={{ p: 4, borderRadius: 3 }}>
            <DropZone onFilesAdded={addFiles} disabled={isProcessing || isDone} />
            <FileList
              files={state.files}
              onRemove={removeFile}
              disabled={isProcessing}
            />

            {state.files.length > 0 && !isDone && (
              <>
                <Divider sx={{ my: 3 }} />
                <TextField
                  fullWidth
                  label="Focus area (optional)"
                  placeholder="e.g. financial projections, technical architecture, risks..."
                  value={focusPrompt}
                  onChange={(e) => setFocusPrompt(e.target.value)}
                  disabled={isProcessing}
                  size="small"
                  helperText="Guide the AI to emphasize specific topics"
                  sx={{ mb: 2 }}
                />
                <Button
                  variant="contained"
                  fullWidth
                  size="large"
                  onClick={() => run(focusPrompt)}
                  disabled={isProcessing || state.files.length === 0}
                >
                  {isProcessing ? 'Processing…' : 'Generate Summary PDF'}
                </Button>
              </>
            )}

            {(isProcessing || isDone) && (
              <ProcessingStatus
                activeStep={state.activeStep}
                steps={STEPS}
                status={state.status}
                totalChunks={state.totalChunks}
              />
            )}

            <ErrorAlert message={state.error} onDismiss={dismissError} />
          </Paper>

          {isDone && (
            <ResultCard
              downloadUrl={state.downloadUrl}
              pdfFilename={state.pdfFilename}
              summaryPreview={state.summaryPreview}
              onReset={reset}
            />
          )}
        </Container>
      </Box>
    </ThemeProvider>
  )
}
