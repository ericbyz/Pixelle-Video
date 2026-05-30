import apiClient from './client'
import type { AppConfig } from '@/types'

/** Get current configuration */
export function getConfig() {
  return apiClient.get<AppConfig>('/config')
}

/** Save configuration */
export function saveConfig(config: Partial<AppConfig>) {
  return apiClient.put('/config', config)
}

/** Test LLM connection with specific params */
export function testLLMConnectionWithParams(params: {
  api_key?: string
  base_url?: string
  model?: string
}) {
  return apiClient.post('/config/test-llm', params)
}

/** Get LLM presets (vendor list) */
export function getLLMPresets() {
  return apiClient.get('/config/llm-presets')
}

/** Fetch available models from LLM API */
export function getLLMModels(params?: { api_key?: string; base_url?: string }) {
  return apiClient.get('/config/llm-models', { params })
}

/** Test LLM connection with current config */
export function testLLMConnection() {
  return apiClient.post('/config/test-llm', {})
}

/** Get image generation service presets */
export function getImagePresets() {
  return apiClient.get('/config/image-presets')
}

/** Get video generation service presets */
export function getVideoPresets() {
  return apiClient.get('/config/video-presets')
}
