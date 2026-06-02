import { useRef, useState } from 'react'
import { Box, Button, Typography } from '@mui/material'
import CloudUploadOutlinedIcon from '@mui/icons-material/CloudUploadOutlined'
import { alpha } from '@mui/material/styles'

const ACCEPTED = '.pdf,.pptx,.ppt'

interface DropZoneProps {
  onFilesAdded: (files: FileList | File[]) => void
  disabled?: boolean
}

/** Drag-and-drop and browse upload area for PDF/PPTX files. */
export default function DropZone({ onFilesAdded, disabled }: DropZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    if (disabled) return
    const files = Array.from(e.dataTransfer.files).filter((f) =>
      /\.(pdf|pptx|ppt)$/i.test(f.name),
    )
    if (files.length) onFilesAdded(files)
  }

  return (
    <Box
      onDragEnter={() => !disabled && setDragging(true)}
      onDragLeave={() => setDragging(false)}
      onDragOver={(e) => e.preventDefault()}
      onDrop={handleDrop}
      onClick={() => !disabled && inputRef.current?.click()}
      sx={{
        position: 'relative',
        borderRadius: 3,
        py: { xs: 5, sm: 7 },
        px: 3,
        textAlign: 'center',
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.45 : 1,
        transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
        border: '2px dashed',
        borderColor: dragging
          ? 'primary.main'
          : alpha('#FFFFFF', 0.15),
        bgcolor: dragging
          ? alpha('#7C5CFF', 0.12)
          : alpha('#FFFFFF', 0.02),
        '&:hover': !disabled
          ? {
              borderColor: 'primary.main',
              bgcolor: alpha('#7C5CFF', 0.08),
              transform: 'translateY(-2px)',
            }
          : {},
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED}
        multiple
        hidden
        onChange={(e) => {
          if (e.target.files?.length) onFilesAdded(e.target.files)
        }}
      />

      <Box
        sx={{
          width: 72,
          height: 72,
          mx: 'auto',
          mb: 2,
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: dragging
            ? 'linear-gradient(135deg, #7C5CFF 0%, #22D3EE 100%)'
            : alpha('#FFFFFF', 0.06),
          transition: 'background 0.25s ease',
        }}
      >
        <CloudUploadOutlinedIcon
          sx={{
            fontSize: 36,
            color: dragging ? '#fff' : 'primary.light',
          }}
        />
      </Box>

      <Typography variant="h6" sx={{ fontWeight: 700, mb: 0.5 }}>
        {dragging ? 'Drop to upload' : 'Drop files here'}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2.5, maxWidth: 320, mx: 'auto' }}>
        PDF or PowerPoint — up to 10 files, 50MB each
      </Typography>
      <Button
        variant="outlined"
        size="medium"
        disabled={disabled}
        onClick={(e) => e.stopPropagation()}
        sx={{
          borderColor: alpha('#FFFFFF', 0.2),
          color: 'text.primary',
          '&:hover': { borderColor: 'primary.main', bgcolor: alpha('#7C5CFF', 0.1) },
        }}
      >
        Browse files
      </Button>
    </Box>
  )
}
