import apiClient from './client'
import type { AppConfig } from '@/types'

/** Get current configuration */
export function getConfig() {
  return apiClient.get<AppConfig>('/config')
}

/** Save configuration */
export function saveConfig(config: Partial<AppConfig>) {
  return apiClient.post('/config', config)
}

/** Test LLM connection */
export function testLLMConnection() {
  return apiClient.post('/llm/chat', {
    prompt: 'Hello, this is a connection test.',
    temperature: 0.1,
    max_tokens: 10,
  })
}
