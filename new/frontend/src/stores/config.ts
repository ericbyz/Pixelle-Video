import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { LLMConfig, ComfyUIConfig } from '@/types'

export const useConfigStore = defineStore('config', () => {
  const llm = ref<LLMConfig>({
    api_key: '',
    base_url: '',
    model: '',
  })

  const comfyui = ref<ComfyUIConfig>({
    comfyui_url: 'http://127.0.0.1:8188',
    comfyui_api_key: '',
    runninghub_api_key: '',
    runninghub_concurrent_limit: 1,
    runninghub_instance_type: '24g',
  })

  const isConfigured = ref(false)
  const isLoading = ref(false)

  const loadConfig = (config: { llm?: LLMConfig; comfyui?: ComfyUIConfig }) => {
    if (config.llm) {
      Object.assign(llm.value, config.llm)
    }
    if (config.comfyui) {
      Object.assign(comfyui.value, config.comfyui)
    }
    isConfigured.value = !!(llm.value.api_key && llm.value.base_url && llm.value.model)
  }

  return {
    llm,
    comfyui,
    isConfigured,
    isLoading,
    loadConfig,
  }
})
