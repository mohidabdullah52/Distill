import { Alert, AlertTitle, Box, Button } from '@mui/material'

interface ErrorAlertProps {
  message: string | null
  onDismiss: () => void
}

export default function ErrorAlert({ message, onDismiss }: ErrorAlertProps) {
  if (!message) return null
  return (
    <Box sx={{ mt: 3 }}>
      <Alert
        severity="error"
        action={
          <Button color="inherit" size="small" onClick={onDismiss}>
            Dismiss
          </Button>
        }
      >
        <AlertTitle>Error</AlertTitle>
        {message}
      </Alert>
    </Box>
  )
}
