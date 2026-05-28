import apiClient from './client'

/** Upload file */
export function uploadFile(file: File, path?: string) {
  const formData = new FormData()
  formData.append('file', file)
  if (path) {
    formData.append('path', path)
  }
  return apiClient.post('/files/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

/** Get file URL */
export function getFileUrl(filePath: string): string {
  return `/api/files/${filePath}`
}
