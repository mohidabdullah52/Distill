import { Box, Chip, Typography } from '@mui/material'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import SlideshowIcon from '@mui/icons-material/Slideshow'

interface FileListProps {
  files: File[]
  onRemove: (index: number) => void
  disabled?: boolean
}

function getIcon(name: string) {
  return /\.pdf$/i.test(name) ? (
    <PictureAsPdfIcon fontSize="small" />
  ) : (
    <SlideshowIcon fontSize="small" />
  )
}

export default function FileList({ files, onRemove, disabled }: FileListProps) {
  if (!files.length) return null
  return (
    <Box sx={{ mt: 2 }}>
      <Typography
        variant="caption"
        color="text.secondary"
        sx={{ mb: 0.5, display: 'block' }}
      >
        {files.length} file{files.length > 1 ? 's' : ''} selected
      </Typography>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
        {files.map((f, i) => (
          <Chip
            key={`${f.name}-${i}`}
            icon={getIcon(f.name)}
            label={f.name}
            onDelete={disabled ? undefined : () => onRemove(i)}
            color="primary"
            variant="outlined"
            size="small"
          />
        ))}
      </Box>
    </Box>
  )
}
