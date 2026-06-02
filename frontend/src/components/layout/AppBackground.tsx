import { Box } from '@mui/material'
import { alpha } from '@mui/material/styles'

/** Animated gradient mesh behind the application shell. */
export default function AppBackground() {
  return (
    <Box
      aria-hidden
      sx={{
        position: 'fixed',
        inset: 0,
        zIndex: 0,
        overflow: 'hidden',
        pointerEvents: 'none',
        bgcolor: '#07080F',
      }}
    >
      <Box
        sx={{
          position: 'absolute',
          top: '-20%',
          left: '-10%',
          width: '55%',
          height: '55%',
          borderRadius: '50%',
          background: `radial-gradient(circle, ${alpha('#7C5CFF', 0.35)} 0%, transparent 70%)`,
          animation: 'pulse-glow 8s ease-in-out infinite',
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          bottom: '-15%',
          right: '-5%',
          width: '50%',
          height: '50%',
          borderRadius: '50%',
          background: `radial-gradient(circle, ${alpha('#22D3EE', 0.22)} 0%, transparent 70%)`,
          animation: 'pulse-glow 10s ease-in-out infinite 1s',
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          top: '40%',
          right: '30%',
          width: '25%',
          height: '25%',
          borderRadius: '50%',
          background: `radial-gradient(circle, ${alpha('#5B8DEF', 0.15)} 0%, transparent 70%)`,
          animation: 'float 12s ease-in-out infinite',
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          inset: 0,
          backgroundImage: `radial-gradient(${alpha('#FFFFFF', 0.04)} 1px, transparent 1px)`,
          backgroundSize: '32px 32px',
          maskImage: 'linear-gradient(to bottom, black 0%, transparent 100%)',
        }}
      />
    </Box>
  )
}
