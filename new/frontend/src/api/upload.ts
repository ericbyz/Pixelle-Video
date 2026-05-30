import apiClient from './client'
import type { UploadResponse } from '@/types'

/** Upload file (image/video/audio) */
export function uploadFile(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return apiClient.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }) as unknown as Promise<UploadResponse>
}

/** Get file URL for serving */
export function getFileUrl(filePath: string): string {
  return `/api/files/${filePath}`
}
