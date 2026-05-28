import { ref, onUnmounted } from 'vue'

export interface WSMessage {
  type: string
  data: any
}

export function useWebSocket(url: string) {
  const ws = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const lastMessage = ref<WSMessage | null>(null)
  const error = ref<Event | null>(null)
  const reconnectAttempts = ref(0)

  const maxReconnectAttempts = 5
  const reconnectDelay = 3000

  let reconnectTimer: ReturnType<typeof setTimeout> | null = null

  const connect = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = url.startsWith('ws') ? url : `${protocol}//${window.location.host}${url}`

    ws.value = new WebSocket(wsUrl)

    ws.value.onopen = () => {
      isConnected.value = true
      reconnectAttempts.value = 0
    }

    ws.value.onmessage = (event) => {
      try {
        lastMessage.value = JSON.parse(event.data)
      } catch {
        lastMessage.value = { type: 'raw', data: event.data }
      }
    }

    ws.value.onclose = () => {
      isConnected.value = false
      if (reconnectAttempts.value < maxReconnectAttempts) {
        reconnectTimer = setTimeout(() => {
          reconnectAttempts.value++
          connect()
        }, reconnectDelay)
      }
    }

    ws.value.onerror = (e) => {
      error.value = e
    }
  }

  const disconnect = () => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    ws.value?.close()
    ws.value = null
    isConnected.value = false
  }

  const send = (data: any) => {
    if (ws.value?.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify(data))
    }
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    ws,
    isConnected,
    lastMessage,
    error,
    connect,
    disconnect,
    send,
  }
}
