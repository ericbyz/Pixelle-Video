import apiClient from './client'
import type {
  VideoGenerateRequest,
  VideoGenerateResponse,
  VideoGenerateAsyncResponse,
} from '@/types'

/** Generate video synchronously */
export function generateVideoSync(data: VideoGenerateRequest) {
  return apiClient.post<VideoGenerateResponse>('/video/generate/sync', data)
}

/** Generate video asynchronously */
export function generateVideoAsync(data: VideoGenerateRequest) {
  return apiClient.post<VideoGenerateAsyncResponse>('/video/generate/async', data)
}
