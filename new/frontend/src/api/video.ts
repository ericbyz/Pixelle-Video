import apiClient from './client'
import type {
  VideoGenerateRequest,
  VideoGenerateResponse,
  VideoGenerateAsyncResponse,
} from '@/types'

/** Generate video synchronously */
export function generateVideoSync(data: VideoGenerateRequest) {
  return apiClient.post('/video/generate/sync', data) as unknown as Promise<VideoGenerateResponse>
}

/** Generate video asynchronously */
export function generateVideoAsync(data: VideoGenerateRequest) {
  return apiClient.post('/video/generate/async', data) as unknown as Promise<VideoGenerateAsyncResponse>
}
