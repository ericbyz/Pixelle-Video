import { ref, computed, watch, type Ref } from 'vue'
import { useWebSocket } from './useWebSocket'
import type { TaskProgress, TaskStatus } from '@/types'

export function useProgress(taskId: Ref<string | null>) {
  const progress = ref<TaskProgress | null>(null)
  const status = ref<TaskStatus>('pending')
  const errorMessage = ref<string | null>(null)
  const result = ref<any>(null)

  const percentage = computed(() => progress.value?.percentage ?? 0)
  const message = computed(() => progress.value?.message ?? '')
  const isRunning = computed(() => status.value === 'running')
  const isCompleted = computed(() => status.value === 'completed')
  const isFailed = computed(() => status.value === 'failed')

  const { isConnected, lastMessage, connect, disconnect } = useWebSocket('/ws')

  const startTracking = (id: string) => {
    taskId.value = id
    status.value = 'running'
    progress.value = null
    errorMessage.value = null
    result.value = null

    // Connect to WebSocket for real-time updates
    if (!isConnected.value) {
      connect()
    }
  }

  const stopTracking = () => {
    status.value = 'completed'
    disconnect()
  }

  // Watch for WebSocket messages
  watch(lastMessage, (msg) => {
    if (!msg || !taskId.value) return

    if (msg.type === 'progress' && msg.data?.task_id === taskId.value) {
      progress.value = msg.data
    } else if (msg.type === 'complete' && msg.data?.task_id === taskId.value) {
      status.value = 'completed'
      result.value = msg.data?.result
      disconnect()
    } else if (msg.type === 'error' && msg.data?.task_id === taskId.value) {
      status.value = 'failed'
      errorMessage.value = msg.data?.error
      disconnect()
    }
  })

  return {
    progress,
    status,
    errorMessage,
    result,
    percentage,
    message,
    isRunning,
    isCompleted,
    isFailed,
    isConnected,
    startTracking,
    stopTracking,
  }
}
