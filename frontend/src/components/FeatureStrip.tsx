import { Box, Typography } from '@mui/material'
import DescriptionIcon from '@mui/icons-material/Description'
import HubIcon from '@mui/icons-material/Hub'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import PsychologyIcon from '@mui/icons-material/Psychology'
import { alpha } from '@mui/material/styles'

const FEATURES = [
  { icon: DescriptionIcon, label: 'PDF & PPTX ingest' },
  { icon: HubIcon, label: 'ChromaDB retrieval' },
  { icon: PsychologyIcon, label: 'AI synthesis' },
  { icon: PictureAsPdfIcon, label: 'Export summary PDF' },
] as const

/** Horizontal feature highlights below the hero. */
export default function FeatureStrip() {
  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: { xs: '1fr 1fr', md: 'repeat(4, 1fr)' },
        gap: 1.5,
        mb: 3,
      }}
    >
      {FEATURES.map(({ icon: Icon, label }) => (
        <Box
          key={label}
          sx={{
            p: 1.5,
            borderRadius: 2,
            border: `1px solid ${alpha('#FFFFFF', 0.06)}`,
            bgcolor: alpha('#FFFFFF', 0.03),
            display: 'flex',
            alignItems: 'center',
            gap: 1,
          }}
        >
          <Icon sx={{ fontSize: 20, color: 'secondary.main', opacity: 0.9 }} />
          <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
            {label}
          </Typography>
        </Box>
      ))}
    </Box>
  )
}
