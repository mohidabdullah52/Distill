import axios from 'axios'

export interface HealthResponse {
  status: string
  provider?: string
  model?: string
  llm_config_error?: string
}

const healthClient = axios.create({
  baseURL: '/',
  timeout: 10000,
})

/** Fetch backend health and LLM provider metadata. */
export async function fetchHealth(): Promise<HealthResponse> {
  const { data } = await healthClient.get<HealthResponse>('/health')
  return data
}
