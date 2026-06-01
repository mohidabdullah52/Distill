import { useRef, useState } from 'react'
import { Box, Button, Typography } from '@mui/material'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'

const ACCEPTED = '.pdf,.pptx,.ppt'

interface DropZoneProps {
  onFilesAdded: (files: FileList | File[]) => void
  disabled?: boolean
}

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
        border: '2px dashed',
        borderColor: dragging ? 'primary.main' : 'grey.300',
        borderRadius: 3,
        py: 6,
        px: 4,
        textAlign: 'center',
        cursor: disabled ? 'not-allowed' : 'pointer',
        transition: 'all 0.2s ease',
        bgcolor: dragging ? 'primary.light' : 'background.paper',
        opacity: disabled ? 0.5 : 1,
        '&:hover': !disabled
          ? { borderColor: 'primary.main', bgcolor: 'primary.light' }
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
      <CloudUploadIcon sx={{ fontSize: 52, color: 'primary.main', mb: 1 }} />
      <Typography variant="h6" gutterBottom>
        Drag & drop files here
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Supports PDF and PPTX — up to 10 files
      </Typography>
      <Button variant="outlined" size="small" disabled={disabled}>
        Browse Files
      </Button>
    </Box>
  )
}
