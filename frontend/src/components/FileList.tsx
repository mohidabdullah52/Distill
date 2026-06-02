import { Box, Chip, IconButton, Typography } from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import SlideshowIcon from '@mui/icons-material/Slideshow'
import { alpha } from '@mui/material/styles'

interface FileListProps {
  files: File[]
  onRemove: (index: number) => void
  disabled?: boolean
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function getIcon(name: string) {
  return /\.pdf$/i.test(name) ? (
    <PictureAsPdfIcon fontSize="small" />
  ) : (
    <SlideshowIcon fontSize="small" />
  )
}

/** List of selected files with size and remove actions. */
export default function FileList({ files, onRemove, disabled }: FileListProps) {
  if (!files.length) return null

  return (
    <Box sx={{ mt: 2.5 }}>
      <Typography
        variant="overline"
        sx={{ color: 'text.secondary', letterSpacing: '0.12em', fontWeight: 700 }}
      >
        {files.length} file{files.length > 1 ? 's' : ''} selected
      </Typography>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mt: 1 }}>
        {files.map((f, i) => (
          <Box
            key={`${f.name}-${f.size}-${i}`}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1.5,
              p: 1.25,
              pr: 0.5,
              borderRadius: 2,
              bgcolor: alpha('#FFFFFF', 0.04),
              border: `1px solid ${alpha('#FFFFFF', 0.06)}`,
            }}
          >
            <Chip
              icon={getIcon(f.name)}
              label={f.name}
              size="small"
              sx={{
                flex: 1,
                justifyContent: 'flex-start',
                maxWidth: '100%',
                bgcolor: 'transparent',
                border: 'none',
                '& .MuiChip-label': { overflow: 'hidden', textOverflow: 'ellipsis' },
              }}
            />
            <Typography variant="caption" color="text.secondary" sx={{ flexShrink: 0 }}>
              {formatSize(f.size)}
            </Typography>
            {!disabled && (
              <IconButton
                size="small"
                aria-label={`Remove ${f.name}`}
                onClick={() => onRemove(i)}
                sx={{ color: 'text.secondary' }}
              >
                <CloseIcon fontSize="small" />
              </IconButton>
            )}
          </Box>
        ))}
      </Box>
    </Box>
  )
}
