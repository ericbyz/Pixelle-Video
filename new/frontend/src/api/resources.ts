import apiClient from './client'
import type {
  WorkflowListResponse,
  TemplateListResponse,
  TemplateParamsResponse,
  BGMListResponse,
} from '@/types'

/** List TTS workflows */
export function listTTSWorkflows() {
  return apiClient.get('/resources/workflows/tts') as unknown as Promise<WorkflowListResponse>
}

/** List media workflows (image + video) */
export function listMediaWorkflows() {
  return apiClient.get('/resources/workflows/media') as unknown as Promise<WorkflowListResponse>
}

/** List image workflows */
export function listImageWorkflows() {
  return apiClient.get('/resources/workflows/image') as unknown as Promise<WorkflowListResponse>
}

/** List templates */
export function listTemplates() {
  return apiClient.get('/resources/templates') as unknown as Promise<TemplateListResponse>
}

/** Get template params */
export function getTemplateParams(template: string) {
  return apiClient.get('/frame/template/params', {
    params: { template },
  }) as unknown as Promise<TemplateParamsResponse>
}

/** List BGM files */
export function listBGM() {
  return apiClient.get('/resources/bgm') as unknown as Promise<BGMListResponse>
}
