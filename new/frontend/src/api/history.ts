import apiClient from './client'
import type { Task } from '@/types'

/** List tasks */
export function listTasks(params?: { status?: string; limit?: number }) {
  return apiClient.get<Task[]>('/tasks', { params })
}

/** Get task detail */
export function getTask(taskId: string) {
  return apiClient.get<Task>(`/tasks/${taskId}`)
}

/** Cancel task */
export function cancelTask(taskId: string) {
  return apiClient.delete(`/tasks/${taskId}`)
}
