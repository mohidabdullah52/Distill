import { alpha, createTheme } from '@mui/material/styles'

const accent = '#7C5CFF'
const accentSecondary = '#22D3EE'

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: accent,
      light: '#A78BFA',
      dark: '#5B3FD9',
    },
    secondary: {
      main: accentSecondary,
      dark: '#0891B2',
    },
    success: {
      main: '#34D399',
    },
    error: {
      main: '#F87171',
    },
    background: {
      default: '#07080F',
      paper: alpha('#12141F', 0.72),
    },
    text: {
      primary: '#F4F4F8',
      secondary: alpha('#F4F4F8', 0.62),
    },
    divider: alpha('#FFFFFF', 0.08),
  },
  typography: {
    fontFamily: '"Plus Jakarta Sans", "DM Sans", system-ui, sans-serif',
    h1: {
      fontWeight: 800,
      letterSpacing: '-0.03em',
      lineHeight: 1.1,
    },
    h2: {
      fontWeight: 700,
      letterSpacing: '-0.02em',
    },
    h4: {
      fontWeight: 700,
      letterSpacing: '-0.02em',
    },
    h6: {
      fontWeight: 600,
    },
    button: {
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 16,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundColor: '#07080F',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 12,
          padding: '10px 22px',
        },
      },
      variants: [
        {
          props: { variant: 'contained', color: 'primary' },
          style: {
            background: `linear-gradient(135deg, ${accent} 0%, #5B8DEF 100%)`,
            boxShadow: `0 8px 32px ${alpha(accent, 0.35)}`,
            '&:hover': {
              background: `linear-gradient(135deg, #8B6FFF 0%, #6B9AF5 100%)`,
            },
          },
        },
      ],
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          fontWeight: 500,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 12,
            backgroundColor: alpha('#FFFFFF', 0.04),
          },
        },
      },
    },
    MuiStepIcon: {
      styleOverrides: {
        root: {
          '&.Mui-completed': {
            color: accentSecondary,
          },
          '&.Mui-active': {
            color: accent,
          },
        },
      },
    },
  },
})

export const glassCard = {
  background: alpha('#161822', 0.65),
  backdropFilter: 'blur(20px)',
  border: `1px solid ${alpha('#FFFFFF', 0.08)}`,
  borderRadius: 3,
  boxShadow: `0 24px 80px ${alpha('#000000', 0.45)}`,
} as const

export default theme
