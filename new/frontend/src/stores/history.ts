import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Task, TaskStatus } from '@/types'
import { listTasks, getTask, cancelTask } from '@/api/history'

export const useHistoryStore = defineStore('history', () => {
  const tasks = ref<Task[]>([])
  const isLoading = ref(false)
  const filterStatus = ref<TaskStatus | ''>('')
  const currentPage = ref(1)
  const pageSize = ref(10)

  const filteredTasks = computed(() => {
    if (!filterStatus.value) return tasks.value
    return tasks.value.filter((t) => t.status === filterStatus.value)
  })

  const pagedTasks = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value
    return filteredTasks.value.slice(start, start + pageSize.value)
  })

  const totalCount = computed(() => filteredTasks.value.length)

  const completedCount = computed(
    () => tasks.value.filter((t) => t.status === 'completed').length
  )

  const failedCount = computed(
    () => tasks.value.filter((t) => t.status === 'failed').length
  )

  const filePathToUrl = (filePath?: string | null) => {
    if (!filePath) return ''
    if (/^https?:\/\//.test(filePath)) return filePath

    const normalized = filePath.replace(/\\/g, '/')
    const outputMarker = '/output/'
    const markerIndex = normalized.indexOf(outputMarker)
    if (markerIndex >= 0) {
      return `/api/files/${normalized.slice(markerIndex + outputMarker.length)}`
    }
    if (normalized.startsWith('output/')) {
      return `/api/files/${normalized.slice('output/'.length)}`
    }
    return `/api/files/${normalized}`
  }

  const normalizeTask = (raw: any): Task => {
    const metadata = raw?.metadata || raw
    const input = metadata?.input || metadata?.request_params || {}
    const result = metadata?.result || {}
    const videoUrl =
      result.video_url ||
      metadata.video_url ||
      filePathToUrl(result.video_path || metadata.video_path)

    return {
      task_id: metadata.task_id,
      task_type: 'video_generation',
      status: metadata.status || 'completed',
      progress: null,
      result: {
        ...result,
        video_url: videoUrl,
        duration: result.duration ?? metadata.duration,
        file_size: result.file_size ?? metadata.file_size,
      },
      error: metadata.error || null,
      created_at: metadata.created_at || '',
      started_at: metadata.started_at || null,
      completed_at: metadata.completed_at || null,
      request_params: {
        ...input,
        text: input.text || metadata.title || '',
        n_scenes: input.n_scenes || metadata.n_frames,
      },
    }
  }

  const fetchTasks = async () => {
    isLoading.value = true
    try {
      const data = await listTasks({ limit: 200 })
      tasks.value = data.tasks.map(normalizeTask)
    } finally {
      isLoading.value = false
    }
  }

  const fetchTaskDetail = async (taskId: string) => {
    const data = await getTask(taskId)
    return normalizeTask(data)
  }

  const removeTask = async (taskId: string) => {
    await cancelTask(taskId)
    tasks.value = tasks.value.filter((t) => t.task_id !== taskId)
  }

  return {
    tasks,
    isLoading,
    filterStatus,
    currentPage,
    pageSize,
    filteredTasks,
    pagedTasks,
    totalCount,
    completedCount,
    failedCount,
    fetchTasks,
    fetchTaskDetail,
    removeTask,
  }
})
