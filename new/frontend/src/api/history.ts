import apiClient from './client'
import type { Task } from '@/types'

export interface HistoryTaskListResponse {
  success: boolean
  tasks: any[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface HistoryTaskDetailResponse {
  success: boolean
  metadata: any
  storyboard?: any
}

/** List tasks */
export function listTasks(params?: { status?: string; limit?: number }) {
  return apiClient.get('/history/tasks', {
    params: {
      status: params?.status || undefined,
      page: 1,
      page_size: params?.limit || 200,
    },
  }) as unknown as Promise<HistoryTaskListResponse>
}

/** Get task detail */
export function getTask(taskId: string) {
  return apiClient.get(`/history/tasks/${taskId}`) as unknown as Promise<HistoryTaskDetailResponse>
}

/** Cancel task */
export function cancelTask(taskId: string) {
  return apiClient.delete(`/history/tasks/${taskId}`) as unknown as Promise<{ success: boolean; message: string }>
}
