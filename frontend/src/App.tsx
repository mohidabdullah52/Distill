import { useState } from 'react'
import {
  Box,
  Button,
  Container,
  CssBaseline,
  Grid,
  Paper,
  TextField,
  ThemeProvider,
  Typography,
} from '@mui/material'
import BoltIcon from '@mui/icons-material/Bolt'
import { alpha } from '@mui/material/styles'
import theme, { glassCard } from './theme'
import AppBackground from './components/layout/AppBackground'
import Header from './components/layout/Header'
import FeatureStrip from './components/FeatureStrip'
import DropZone from './components/DropZone'
import FileList from './components/FileList'
import ProcessingStatus from './components/ProcessingStatus'
import ResultCard from './components/ResultCard'
import ErrorAlert from './components/ErrorAlert'
import { useDocumentPipeline } from './hooks/useDocumentPipeline'
import { useBackendHealth } from './hooks/useBackendHealth'

export default function App() {
  const { state, STEPS, addFiles, removeFile, run, reset, dismissError } =
    useDocumentPipeline()
  const { health, loading: healthLoading } = useBackendHealth()
  const [focusPrompt, setFocusPrompt] = useState('')

  const isProcessing = ['uploading', 'ingesting', 'summarizing'].includes(
    state.status,
  )
  const isDone = state.status === 'done'
  const showWorkspace = state.files.length > 0 || isProcessing || isDone

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBackground />
      <Box sx={{ position: 'relative', zIndex: 1, minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <Header health={health} healthLoading={healthLoading} />

        <Container maxWidth="lg" sx={{ flex: 1, py: { xs: 4, md: 6 }, px: { xs: 2, sm: 3 } }}>
          <Box
            className="animate-fade-up"
            sx={{ textAlign: { xs: 'center', md: 'left' }, mb: { xs: 4, md: 5 } }}
          >
            <Typography
              variant="h1"
              sx={{
                fontSize: { xs: '2.25rem', sm: '3rem', md: '3.5rem' },
                background: 'linear-gradient(135deg, #F4F4F8 0%, #A78BFA 50%, #22D3EE 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                mb: 1.5,
              }}
            >
              Drop files in,
              <br />
              get wisdom out.
            </Typography>
            <Typography
              variant="body1"
              color="text.secondary"
              sx={{ maxWidth: 520, mx: { xs: 'auto', md: 0 }, fontSize: '1.1rem', lineHeight: 1.7 }}
            >
              Upload PDFs or decks. Distill indexes them with RAG, synthesizes a sharp summary, and
              delivers a polished PDF.
            </Typography>
          </Box>

          <FeatureStrip />

          <Grid container spacing={3}>
            <Grid size={{ xs: 12, lg: showWorkspace ? 7 : 12 }}>
              <Paper
                elevation={0}
                sx={{
                  ...glassCard,
                  p: { xs: 2.5, sm: 4 },
                }}
              >
                <Typography variant="overline" sx={{ color: 'primary.light', fontWeight: 700, letterSpacing: '0.14em' }}>
                  Upload
                </Typography>
                <Typography variant="h5" sx={{ fontWeight: 700, mb: 2.5 }}>
                  Your documents
                </Typography>

                <DropZone onFilesAdded={addFiles} disabled={isProcessing || isDone} />
                <FileList
                  files={state.files}
                  onRemove={removeFile}
                  disabled={isProcessing}
                />

                {state.files.length > 0 && !isDone && (
                  <Box sx={{ mt: 3 }}>
                    <TextField
                      fullWidth
                      label="Focus area"
                      placeholder="e.g. revenue trends, security risks, roadmap…"
                      value={focusPrompt}
                      onChange={(e) => setFocusPrompt(e.target.value)}
                      disabled={isProcessing}
                      multiline
                      minRows={2}
                      helperText="Optional — steer the AI toward what matters most"
                      sx={{ mb: 2.5 }}
                    />
                    <Button
                      variant="contained"
                      fullWidth
                      size="large"
                      startIcon={<BoltIcon />}
                      onClick={() => run(focusPrompt)}
                      disabled={isProcessing}
                      sx={{
                        py: 1.5,
                        fontSize: '1rem',
                        ...(isProcessing && {
                          background: alpha('#7C5CFF', 0.5),
                        }),
                      }}
                    >
                      {isProcessing ? 'Distilling…' : 'Generate summary PDF'}
                    </Button>
                  </Box>
                )}

                <ErrorAlert message={state.error} onDismiss={dismissError} />
              </Paper>
            </Grid>

            {(showWorkspace || isDone) && (
              <Grid size={{ xs: 12, lg: 5 }}>
                {(isProcessing || isDone) && (
                  <ProcessingStatus
                    activeStep={state.activeStep}
                    steps={STEPS}
                    status={state.status}
                    totalChunks={state.totalChunks}
                  />
                )}

                {isDone && (
                  <ResultCard
                    downloadUrl={state.downloadUrl}
                    pdfFilename={state.pdfFilename}
                    summaryPreview={state.summaryPreview}
                    onReset={() => {
                      reset()
                      setFocusPrompt('')
                    }}
                  />
                )}

                {!isProcessing && !isDone && state.files.length > 0 && (
                  <Paper
                    elevation={0}
                    sx={{
                      ...glassCard,
                      p: 3,
                      mt: { xs: 0, lg: 0 },
                    }}
                  >
                    <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>
                      Ready when you are
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.7 }}>
                      Hit <strong>Generate summary PDF</strong> to ingest, retrieve relevant chunks
                      from ChromaDB, and synthesize your report with your configured LLM.
                    </Typography>
                  </Paper>
                )}
              </Grid>
            )}
          </Grid>

          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ display: 'block', textAlign: 'center', mt: 5, opacity: 0.6 }}
          >
            Distill · RAG-powered document summarization
          </Typography>
        </Container>
      </Box>
    </ThemeProvider>
  )
}
