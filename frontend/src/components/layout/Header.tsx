import { AppBar, Box, Chip, Toolbar, Typography } from '@mui/material'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import CircleIcon from '@mui/icons-material/Circle'
import { alpha } from '@mui/material/styles'
import type { HealthResponse } from '../../api/health'

interface HeaderProps {
  health: HealthResponse | null
  healthLoading: boolean
}

/**
 * Renders the top navigation bar with branding and backend status chips.
 *
 * @param {HeaderProps} props - Health payload and loading flag from the API.
 * @returns {JSX.Element} Sticky application header.
 */
export default function Header({ health, healthLoading }: HeaderProps) {
  const isOnline = health?.status === 'ok'
  const llmLabel =
    health?.provider && health?.model
      ? `${health.provider} · ${health.model}`
      : health?.llm_config_error
        ? 'LLM not configured'
        : null

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        bgcolor: alpha('#07080F', 0.6),
        backdropFilter: 'blur(16px)',
        borderBottom: `1px solid ${alpha('#FFFFFF', 0.06)}`,
      }}
    >
      <Toolbar sx={{ maxWidth: 1200, width: '100%', mx: 'auto', gap: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flex: 1 }}>
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: 'linear-gradient(135deg, #7C5CFF 0%, #22D3EE 100%)',
              boxShadow: `0 4px 20px ${alpha('#7C5CFF', 0.4)}`,
            }}
          >
            <AutoAwesomeIcon sx={{ color: '#fff', fontSize: 22 }} />
          </Box>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 800, lineHeight: 1.2 }}>
              Distill
            </Typography>
            <Typography variant="caption" color="text.secondary">
              RAG document summarizer
            </Typography>
          </Box>
        </Box>

        {!healthLoading && (
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', justifyContent: 'flex-end' }}>
            <Chip
              size="small"
              icon={
                <CircleIcon
                  sx={{
                    fontSize: 10,
                    color: isOnline ? 'success.main' : 'error.main',
                  }}
                />
              }
              label={isOnline ? 'API online' : 'API offline'}
              variant="outlined"
              sx={{
                borderColor: alpha('#FFFFFF', 0.12),
                bgcolor: alpha('#FFFFFF', 0.04),
              }}
            />
            {llmLabel && (
              <Chip
                size="small"
                label={llmLabel}
                variant="outlined"
                sx={{
                  borderColor: alpha('#7C5CFF', 0.35),
                  bgcolor: alpha('#7C5CFF', 0.08),
                  maxWidth: 220,
                }}
              />
            )}
          </Box>
        )}
      </Toolbar>
    </AppBar>
  )
}
