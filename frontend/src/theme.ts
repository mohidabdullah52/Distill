import { createTheme } from '@mui/material/styles'

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1565C0',
      light: '#E3F2FD',
      dark: '#0D47A1',
    },
    secondary: {
      main: '#00897B',
    },
    background: {
      default: '#F8FAFD',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#1A1A2E',
      secondary: '#5C6B7A',
    },
  },
  typography: {
    fontFamily: '"DM Sans", "Helvetica Neue", Arial, sans-serif',
    h4: { fontWeight: 700, letterSpacing: '-0.5px' },
    h6: { fontWeight: 600 },
    body2: { lineHeight: 1.7 },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          borderRadius: 8,
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { borderRadius: 6 },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: { backgroundImage: 'none' },
      },
    },
  },
})

export default theme
