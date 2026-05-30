import apiClient from './client'
import type { Task } from '@/types'

/** Get task status */
export function getTaskStatus(taskId: string) {
  return apiClient.get(`/tasks/${taskId}`) as unknown as Promise<Task>
}

/** List all tasks */
export function listTasks(params?: { status?: string; limit?: number }) {
  return apiClient.get('/tasks', { params }) as unknown as Promise<Task[]>
}

/** Cancel a task */
export function cancelTask(taskId: string) {
  return apiClient.delete(`/tasks/${taskId}`)
}
