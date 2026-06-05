import { Box, Typography } from '@mui/material'
import { alpha } from '@mui/material/styles'

interface SummaryPreviewProps {
  text: string
}

function renderTextWithBold(textStr: string) {
  const parts = textStr.split('**')
  return parts.map((part, index) => {
    if (index % 2 === 1) {
      return (
        <Box component="span" key={index} sx={{ fontWeight: 700, color: 'text.primary' }}>
          {part}
        </Box>
      )
    }
    return part
  })
}

/**
 * Renders a scrollable summary preview with simple markdown styling.
 *
 * @param {SummaryPreviewProps} props - Markdown summary text to display.
 * @returns {JSX.Element} Formatted preview panel.
 */
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
        if (trimmed.startsWith('### ')) {
          return (
            <Typography
              key={i}
              variant="body2"
              sx={{
                color: 'primary.light',
                fontWeight: 700,
                mt: i > 0 ? 1 : 0,
                mb: 0.5,
              }}
            >
              {renderTextWithBold(trimmed.slice(4))}
            </Typography>
          )
        }
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
              {renderTextWithBold(trimmed.slice(3))}
            </Typography>
          )
        }
        if (trimmed.startsWith('# ')) {
          return (
            <Typography
              key={i}
              variant="subtitle1"
              sx={{
                color: 'primary.light',
                fontWeight: 800,
                mt: i > 0 ? 2 : 0,
                mb: 0.5,
              }}
            >
              {renderTextWithBold(trimmed.slice(2))}
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
              {renderTextWithBold(trimmed.slice(2))}
            </Typography>
          )
        }
        const numListMatch = trimmed.match(/^(\d+)\.\s+(.*)/)
        if (numListMatch) {
          const num = numListMatch[1]
          const content = numListMatch[2]
          return (
            <Typography
              key={i}
              variant="body2"
              color="text.secondary"
              sx={{ pl: 1.5, py: 0.25, display: 'flex', gap: 1 }}
            >
              <Box component="span" sx={{ color: 'secondary.main', fontWeight: 600 }}>
                {num}.
              </Box>
              {renderTextWithBold(content)}
            </Typography>
          )
        }
        if (!trimmed) return <Box key={i} sx={{ height: 8 }} />
        return (
          <Typography key={i} variant="body2" color="text.secondary" sx={{ py: 0.25 }}>
            {renderTextWithBold(trimmed)}
          </Typography>
        )
      })}
    </Box>
  )
}
