import { Alert, AlertTitle, Box, Button, Collapse } from '@mui/material'
import { alpha } from '@mui/material/styles'

interface ErrorAlertProps {
  message: string | null
  onDismiss: () => void
}

/** Dismissible error alert for pipeline failures. */
export default function ErrorAlert({ message, onDismiss }: ErrorAlertProps) {
  return (
    <Collapse in={Boolean(message)}>
      <Box sx={{ mt: 3 }}>
        <Alert
          severity="error"
          variant="outlined"
          sx={{
            borderRadius: 2,
            bgcolor: alpha('#F87171', 0.08),
            borderColor: alpha('#F87171', 0.35),
            '& .MuiAlert-icon': { color: 'error.main' },
          }}
          action={
            <Button color="inherit" size="small" onClick={onDismiss}>
              Dismiss
            </Button>
          }
        >
          <AlertTitle sx={{ fontWeight: 700 }}>Something went wrong</AlertTitle>
          {message}
        </Alert>
      </Box>
    </Collapse>
  )
}
