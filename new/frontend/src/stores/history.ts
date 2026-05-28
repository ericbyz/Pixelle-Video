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

  const fetchTasks = async () => {
    isLoading.value = true
    try {
      const { data } = await listTasks({ limit: 200 })
      tasks.value = data
    } finally {
      isLoading.value = false
    }
  }

  const fetchTaskDetail = async (taskId: string) => {
    const { data } = await getTask(taskId)
    return data
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
