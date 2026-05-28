import apiClient from './client'
import type { Task } from '@/types'

/** Get task status */
export function getTaskStatus(taskId: string) {
  return apiClient.get<Task>(`/tasks/${taskId}`)
}

/** List all tasks */
export function listTasks(params?: { status?: string; limit?: number }) {
  return apiClient.get<Task[]>('/tasks', { params })
}

/** Cancel a task */
export function cancelTask(taskId: string) {
  return apiClient.delete(`/tasks/${taskId}`)
}
