import {
  Box,
  LinearProgress,
  Step,
  StepLabel,
  Stepper,
  Typography,
} from '@mui/material'

interface ProcessingStatusProps {
  activeStep: number
  steps: readonly string[]
  status: string
  totalChunks: number
}

const STATUS_LABELS: Record<string, string> = {
  uploading: 'Uploading files...',
  ingesting: 'Indexing into vector store...',
  summarizing: 'Generating summary with AI...',
  done: 'Complete!',
}

export default function ProcessingStatus({
  activeStep,
  steps,
  status,
  totalChunks,
}: ProcessingStatusProps) {
  const isActive = ['uploading', 'ingesting', 'summarizing'].includes(status)

  return (
    <Box sx={{ mt: 4 }}>
      <Stepper activeStep={activeStep} alternativeLabel>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {isActive && (
        <Box sx={{ mt: 3 }}>
          <LinearProgress color="primary" />
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ mt: 1, textAlign: 'center' }}
          >
            {STATUS_LABELS[status]}
            {status === 'ingesting' &&
              totalChunks > 0 &&
              ` (${totalChunks} chunks indexed)`}
          </Typography>
        </Box>
      )}
    </Box>
  )
}
