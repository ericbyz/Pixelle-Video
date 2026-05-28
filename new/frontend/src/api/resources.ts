import apiClient from './client'
import type {
  WorkflowListResponse,
  TemplateListResponse,
  TemplateParamsResponse,
  BGMListResponse,
} from '@/types'

/** List TTS workflows */
export function listTTSWorkflows() {
  return apiClient.get<WorkflowListResponse>('/resources/workflows/tts')
}

/** List media workflows (image + video) */
export function listMediaWorkflows() {
  return apiClient.get<WorkflowListResponse>('/resources/workflows/media')
}

/** List image workflows */
export function listImageWorkflows() {
  return apiClient.get<WorkflowListResponse>('/resources/workflows/image')
}

/** List templates */
export function listTemplates() {
  return apiClient.get<TemplateListResponse>('/resources/templates')
}

/** Get template params */
export function getTemplateParams(template: string) {
  return apiClient.get<TemplateParamsResponse>('/frame/template/params', {
    params: { template },
  })
}

/** List BGM files */
export function listBGM() {
  return apiClient.get<BGMListResponse>('/resources/bgm')
}
