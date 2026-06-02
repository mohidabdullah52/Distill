import { Box, Button, Paper, Typography } from '@mui/material'
import DownloadIcon from '@mui/icons-material/Download'
import RestartAltIcon from '@mui/icons-material/RestartAlt'
import TaskAltIcon from '@mui/icons-material/TaskAlt'
import { alpha } from '@mui/material/styles'
import SummaryPreview from './SummaryPreview'
import { glassCard } from '../theme'

interface ResultCardProps {
  downloadUrl: string | null
  pdfFilename: string | null
  summaryPreview: string | null
  onReset: () => void
}

/**
 * Displays the finished summary preview and download actions.
 *
 * @param {ResultCardProps} props - Download URL, preview text, and reset handler.
 * @returns {JSX.Element} Result panel after summarization completes.
 */
export default function ResultCard({
  downloadUrl,
  summaryPreview,
  onReset,
}: ResultCardProps) {
  return (
    <Paper
      className="animate-fade-up"
      elevation={0}
      sx={{
        ...glassCard,
        mt: 3,
        p: { xs: 2.5, sm: 3.5 },
        border: `1px solid ${alpha('#34D399', 0.35)}`,
        background: `linear-gradient(145deg, ${alpha('#34D399', 0.08)} 0%, ${alpha('#161822', 0.8)} 40%)`,
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
        <Box
          sx={{
            width: 44,
            height: 44,
            borderRadius: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            bgcolor: alpha('#34D399', 0.15),
            color: 'success.main',
          }}
        >
          <TaskAltIcon />
        </Box>
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            Summary ready
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Your distilled report is available to download
          </Typography>
        </Box>
      </Box>

      {summaryPreview && (
        <Box sx={{ mb: 2.5 }}>
          <Typography
            variant="overline"
            sx={{ color: 'text.secondary', letterSpacing: '0.1em', mb: 1, display: 'block' }}
          >
            Preview
          </Typography>
          <SummaryPreview text={summaryPreview} />
        </Box>
      )}

      <Box sx={{ display: 'flex', gap: 1.5, flexWrap: 'wrap' }}>
        <Button
          variant="contained"
          size="large"
          startIcon={<DownloadIcon />}
          component="a"
          href={downloadUrl || '#'}
          target="_blank"
          rel="noopener noreferrer"
          disabled={!downloadUrl}
          sx={{ flex: { xs: '1 1 100%', sm: '0 1 auto' } }}
        >
          Download PDF
        </Button>
        <Button
          variant="outlined"
          size="large"
          startIcon={<RestartAltIcon />}
          onClick={onReset}
          sx={{
            flex: { xs: '1 1 100%', sm: '0 1 auto' },
            borderColor: alpha('#FFFFFF', 0.2),
            color: 'text.primary',
          }}
        >
          Start over
        </Button>
      </Box>
    </Paper>
  )
}
