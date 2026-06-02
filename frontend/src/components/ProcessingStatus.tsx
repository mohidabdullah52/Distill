import {
  Box,
  LinearProgress,
  Step,
  StepConnector,
  stepConnectorClasses,
  StepLabel,
  Stepper,
  Typography,
} from '@mui/material'
import { alpha, styled } from '@mui/material/styles'

interface ProcessingStatusProps {
  activeStep: number
  steps: readonly string[]
  status: string
  totalChunks: number
}

const STATUS_LABELS: Record<string, string> = {
  uploading: 'Uploading your documents…',
  ingesting: 'Embedding chunks into ChromaDB…',
  summarizing: 'Synthesizing your summary with AI…',
  done: 'All done — your PDF is ready',
}

const GradientConnector = styled(StepConnector)(() => ({
  [`&.${stepConnectorClasses.alternativeLabel}`]: {
    top: 14,
  },
  [`&.${stepConnectorClasses.active} .${stepConnectorClasses.line}`]: {
    background: 'linear-gradient(90deg, #7C5CFF, #22D3EE)',
  },
  [`&.${stepConnectorClasses.completed} .${stepConnectorClasses.line}`]: {
    background: '#22D3EE',
  },
  [`& .${stepConnectorClasses.line}`]: {
    height: 3,
    border: 0,
    backgroundColor: alpha('#FFFFFF', 0.12),
    borderRadius: 2,
  },
}))

/** Pipeline stepper with progress and status messaging. */
export default function ProcessingStatus({
  activeStep,
  steps,
  status,
  totalChunks,
}: ProcessingStatusProps) {
  const isActive = ['uploading', 'ingesting', 'summarizing'].includes(status)
  const isDone = status === 'done'

  return (
    <Box
      className="animate-fade-up"
      sx={{
        mt: { xs: 3, lg: 0 },
        p: 2.5,
        borderRadius: 2,
        bgcolor: alpha('#FFFFFF', 0.03),
        border: `1px solid ${alpha('#FFFFFF', 0.06)}`,
      }}
    >
      <Stepper
        activeStep={activeStep}
        alternativeLabel
        connector={<GradientConnector />}
      >
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>
              <Typography
                variant="caption"
                sx={{
                  fontWeight: 600,
                  color: 'text.secondary',
                }}
              >
                {label}
              </Typography>
            </StepLabel>
          </Step>
        ))}
      </Stepper>

      {(isActive || isDone) && (
        <Box sx={{ mt: 3 }}>
          {isActive && (
            <LinearProgress
              sx={{
                height: 6,
                borderRadius: 3,
                bgcolor: alpha('#FFFFFF', 0.08),
                '& .MuiLinearProgress-bar': {
                  borderRadius: 3,
                  background: 'linear-gradient(90deg, #7C5CFF, #22D3EE, #7C5CFF)',
                  backgroundSize: '200% 100%',
                  animation: 'shimmer 2s linear infinite',
                },
              }}
            />
          )}
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ mt: 1.5, textAlign: 'center', fontWeight: 500 }}
          >
            {STATUS_LABELS[status]}
            {status === 'ingesting' && totalChunks > 0 && (
              <Box component="span" sx={{ color: 'secondary.main', ml: 0.5 }}>
                ({totalChunks} chunks)
              </Box>
            )}
          </Typography>
        </Box>
      )}
    </Box>
  )
}
