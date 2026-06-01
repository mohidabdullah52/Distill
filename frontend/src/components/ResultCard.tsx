import { Box, Button, Divider, Paper, Typography } from '@mui/material'
import DownloadIcon from '@mui/icons-material/Download'
import RestartAltIcon from '@mui/icons-material/RestartAlt'

interface ResultCardProps {
  downloadUrl: string | null
  pdfFilename: string | null
  summaryPreview: string | null
  onReset: () => void
}

export default function ResultCard({
  downloadUrl,
  pdfFilename: _pdfFilename,
  summaryPreview,
  onReset,
}: ResultCardProps) {
  return (
    <Paper
      elevation={2}
      sx={{
        mt: 4,
        p: 3,
        borderRadius: 3,
        border: '1px solid',
        borderColor: 'success.light',
      }}
    >
      <Typography variant="h6" color="success.dark" gutterBottom>
        Summary ready
      </Typography>

      {summaryPreview && (
        <>
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ mb: 0.5, display: 'block' }}
          >
            Preview
          </Typography>
          <Box
            sx={{
              bgcolor: 'grey.50',
              borderRadius: 2,
              p: 2,
              maxHeight: 160,
              overflow: 'hidden',
              position: 'relative',
              '&::after': {
                content: '""',
                position: 'absolute',
                bottom: 0,
                left: 0,
                right: 0,
                height: 40,
                background: 'linear-gradient(transparent, #F8F9FA)',
              },
            }}
          >
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ whiteSpace: 'pre-wrap' }}
            >
              {summaryPreview}
            </Typography>
          </Box>
          <Divider sx={{ my: 2 }} />
        </>
      )}

      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <Button
          variant="contained"
          startIcon={<DownloadIcon />}
          component="a"
          href={downloadUrl || '#'}
          target="_blank"
          rel="noopener noreferrer"
          disabled={!downloadUrl}
        >
          Download PDF
        </Button>
        <Button variant="outlined" startIcon={<RestartAltIcon />} onClick={onReset}>
          Start Over
        </Button>
      </Box>
    </Paper>
  )
}
