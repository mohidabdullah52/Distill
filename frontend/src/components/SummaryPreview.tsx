import { Box, Typography } from '@mui/material'
import { alpha } from '@mui/material/styles'

interface SummaryPreviewProps {
  text: string
}

/** Renders a scrollable summary preview with basic markdown heading styles. */
export default function SummaryPreview({ text }: SummaryPreviewProps) {
  const lines = text.split('\n')

  return (
    <Box
      sx={{
        maxHeight: 280,
        overflow: 'auto',
        p: 2,
        borderRadius: 2,
        bgcolor: alpha('#000000', 0.25),
        border: `1px solid ${alpha('#FFFFFF', 0.06)}`,
        '&::-webkit-scrollbar': { width: 6 },
        '&::-webkit-scrollbar-thumb': {
          bgcolor: alpha('#FFFFFF', 0.15),
          borderRadius: 3,
        },
      }}
    >
      {lines.map((line, i) => {
        const trimmed = line.trim()
        if (trimmed.startsWith('## ')) {
          return (
            <Typography
              key={i}
              variant="subtitle2"
              sx={{
                color: 'primary.light',
                fontWeight: 700,
                mt: i > 0 ? 1.5 : 0,
                mb: 0.5,
              }}
            >
              {trimmed.slice(3)}
            </Typography>
          )
        }
        if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
          return (
            <Typography
              key={i}
              variant="body2"
              color="text.secondary"
              sx={{ pl: 1.5, py: 0.25, display: 'flex', gap: 1 }}
            >
              <Box component="span" sx={{ color: 'secondary.main' }}>
                •
              </Box>
              {trimmed.slice(2)}
            </Typography>
          )
        }
        if (!trimmed) return <Box key={i} sx={{ height: 8 }} />
        return (
          <Typography key={i} variant="body2" color="text.secondary" sx={{ py: 0.25 }}>
            {trimmed}
          </Typography>
        )
      })}
    </Box>
  )
}
