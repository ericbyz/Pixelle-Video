import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { LLMConfig, ComfyUIConfig, ImageServiceConfig, VideoServiceConfig } from '@/types'
import {
  getConfig,
  saveConfig,
  getLLMPresets,
  getLLMModels,
  testLLMConnectionWithParams,
  testComfyUIConnection,
  getImagePresets,
  getVideoPresets,
} from '@/api/config'

export interface LLMPreset {
  name: string
  base_url: string
  model: string
  api_key_url?: string
  default_api_key?: string
  models?: { id: string; name: string }[]
}

export interface ServicePreset {
  name: string
  provider: string
  base_url: string
  models: { id: string; name: string }[]
  api_key_url?: string
  description?: string
}

export const useConfigStore = defineStore('config', () => {
  // LLM config
  const llm = ref<LLMConfig>({
    api_key: '',
    base_url: '',
    model: '',
  })

  // ComfyUI config
  const comfyui = ref<ComfyUIConfig>({
    comfyui_url: 'http://127.0.0.1:8188',
    comfyui_api_key: '',
    runninghub_api_key: '',
    runninghub_concurrent_limit: 1,
    runninghub_instance_type: '',
  })

  // Image service config
  const imageService = ref<ImageServiceConfig>({
    provider: 'comfyui',
    api_key: '',
    base_url: '',
    model: '',
  })

  // Video service config
  const videoService = ref<VideoServiceConfig>({
    provider: 'comfyui',
    api_key: '',
    base_url: '',
    model: '',
  })

  // LLM presets
  const llmPresets = ref<LLMPreset[]>([])
  const selectedPreset = ref<string>('Custom')

  // Image/Video service presets
  const imagePresets = ref<ServicePreset[]>([])
  const videoPresets = ref<ServicePreset[]>([])
  const selectedImagePreset = ref<string>('')
  const selectedVideoPreset = ref<string>('')

  // Loaded models from API
  const loadedModels = ref<string[]>([])
  const isLoadingModels = ref(false)

  // UI state
  const isConfigured = ref(false)
  const isLoading = ref(false)
  const isSaving = ref(false)
  const isTesting = ref(false)
  const isTestingComfyUI = ref(false)

  // Custom model input (when "Custom..." is selected)
  const customModel = ref('')

  const CUSTOM_MODEL_SENTINEL = '__custom__'

  // Compute preset names including Custom
  const presetNames = computed(() => {
    return [...llmPresets.value.map((p) => p.name), 'Custom']
  })

  // Current model selection: either from loaded models or custom
  const currentModelSelection = computed({
    get: () => {
      if (loadedModels.value.includes(llm.value.model)) {
        return llm.value.model
      }
      return CUSTOM_MODEL_SENTINEL
    },
    set: (value: string) => {
      if (value === CUSTOM_MODEL_SENTINEL) {
        customModel.value = llm.value.model
        return
      }
      llm.value.model = value
      customModel.value = ''
    },
  })

  // Current LLM preset's built-in models (matched by base_url)
  const currentPresetModels = computed(() => {
    const preset = llmPresets.value.find((p) => p.base_url === llm.value.base_url)
    return preset?.models || []
  })

  // Current image preset's models
  const currentImageModels = computed(() => {
    const preset = imagePresets.value.find((p) => p.name === selectedImagePreset.value)
    return preset?.models || []
  })

  // Current video preset's models
  const currentVideoModels = computed(() => {
    const preset = videoPresets.value.find((p) => p.name === selectedVideoPreset.value)
    return preset?.models || []
  })

  // Auto-detect which preset matches current config (by base_url)
  function detectPreset() {
    const match = llmPresets.value.find(
      (p) => p.base_url === llm.value.base_url
    )
    selectedPreset.value = match ? match.name : 'Custom'
  }

  // Apply preset values
  function applyPreset(presetName: string) {
    if (presetName === 'Custom') {
      selectedPreset.value = 'Custom'
      customModel.value = llm.value.model
      return
    }

    const preset = llmPresets.value.find((p) => p.name === presetName)
    if (!preset) return

    selectedPreset.value = presetName
    llm.value.base_url = preset.base_url
    llm.value.model = preset.model

    // If preset has a default_api_key (e.g. Ollama), use it
    if (preset.default_api_key && !llm.value.api_key) {
      llm.value.api_key = preset.default_api_key
    }
  }

  // Apply image preset
  function applyImagePreset(presetName: string) {
    const preset = imagePresets.value.find((p) => p.name === presetName)
    if (!preset) return

    selectedImagePreset.value = presetName
    imageService.value.base_url = preset.base_url
    imageService.value.provider = preset.provider
    if (preset.models.length > 0 && !imageService.value.model) {
      imageService.value.model = preset.models[0].id
    }
  }

  // Apply video preset
  function applyVideoPreset(presetName: string) {
    const preset = videoPresets.value.find((p) => p.name === presetName)
    if (!preset) return

    selectedVideoPreset.value = presetName
    videoService.value.base_url = preset.base_url
    videoService.value.provider = preset.provider
    if (preset.models.length > 0 && !videoService.value.model) {
      videoService.value.model = preset.models[0].id
    }
  }

  // Get current preset's api_key_url
  const currentApiKeyUrl = computed(() => {
    if (selectedPreset.value === 'Custom') return ''
    const preset = llmPresets.value.find((p) => p.name === selectedPreset.value)
    return preset?.api_key_url || ''
  })

  const currentImageApiKeyUrl = computed(() => {
    const preset = imagePresets.value.find((p) => p.name === selectedImagePreset.value)
    return preset?.api_key_url || ''
  })

  const currentVideoApiKeyUrl = computed(() => {
    const preset = videoPresets.value.find((p) => p.name === selectedVideoPreset.value)
    return preset?.api_key_url || ''
  })

  // Load config from API
  async function loadConfig() {
    isLoading.value = true
    try {
      const res: any = await getConfig()
      const data = res.config || res
      if (data.llm) {
        Object.assign(llm.value, data.llm)
      }
      if (data.comfyui) {
        Object.assign(comfyui.value, data.comfyui)
      }
      if (data.image_service) {
        Object.assign(imageService.value, data.image_service)
      }
      if (data.video_service) {
        Object.assign(videoService.value, data.video_service)
      }
      isConfigured.value = !!(llm.value.api_key && llm.value.base_url && llm.value.model)
      detectPreset()
      if (selectedPreset.value === 'Custom') customModel.value = llm.value.model
      detectImagePreset()
      detectVideoPreset()
    } catch (e) {
      console.error('Failed to load config:', e)
    } finally {
      isLoading.value = false
    }
  }

  // Detect image/video presets (by base_url)
  function detectImagePreset() {
    if (!imageService.value.base_url) {
      selectedImagePreset.value = ''
      return
    }
    const match = imagePresets.value.find(
      (p) => p.base_url === imageService.value.base_url
    )
    selectedImagePreset.value = match ? match.name : ''
  }

  function detectVideoPreset() {
    if (!videoService.value.base_url) {
      selectedVideoPreset.value = ''
      return
    }
    const match = videoPresets.value.find(
      (p) => p.base_url === videoService.value.base_url
    )
    selectedVideoPreset.value = match ? match.name : ''
  }

  // Load LLM presets from API
  async function loadPresets() {
    try {
      const res: any = await getLLMPresets()
      llmPresets.value = res.presets || []
      detectPreset()
    } catch (e) {
      console.error('Failed to load presets:', e)
    }
  }

  // Load image presets
  async function loadImagePresets() {
    try {
      const res: any = await getImagePresets()
      imagePresets.value = res.presets || []
      detectImagePreset()
    } catch (e) {
      console.error('Failed to load image presets:', e)
    }
  }

  // Load video presets
  async function loadVideoPresets() {
    try {
      const res: any = await getVideoPresets()
      videoPresets.value = res.presets || []
      detectVideoPreset()
    } catch (e) {
      console.error('Failed to load video presets:', e)
    }
  }

  // Fetch models from API
  async function fetchModels() {
    if (!llm.value.api_key || !llm.value.base_url) {
      throw new Error('Please fill in API Key and Base URL first')
    }
    isLoadingModels.value = true
    try {
      const res: any = await getLLMModels({
        api_key: llm.value.api_key,
        base_url: llm.value.base_url,
      })
      const models = res.models || []
      loadedModels.value = models.map((m: any) => m.id || m.name)
      return loadedModels.value
    } catch (e) {
      console.error('Failed to fetch models:', e)
      throw e
    } finally {
      isLoadingModels.value = false
    }
  }

  // Test LLM connection
  async function testConnection() {
    if (!llm.value.api_key || !llm.value.base_url) {
      throw new Error('Please fill in API Key and Base URL first')
    }
    isTesting.value = true
    try {
      const res: any = await testLLMConnectionWithParams({
        api_key: llm.value.api_key,
        base_url: llm.value.base_url,
        model: llm.value.model,
      })
      return res
    } finally {
      isTesting.value = false
    }
  }

  // Test ComfyUI connection
  async function testComfyUI() {
    isTestingComfyUI.value = true
    try {
      const res: any = await testComfyUIConnection({
        comfyui_url: comfyui.value.comfyui_url,
        comfyui_api_key: comfyui.value.comfyui_api_key,
      })
      return res
    } finally {
      isTestingComfyUI.value = false
    }
  }

  // Save config to API
  async function save() {
    isSaving.value = true
    try {
      const modelToSave = llm.value.model

      await saveConfig({
        llm: {
          ...llm.value,
          model: modelToSave,
        },
        comfyui: comfyui.value,
        image_service: imageService.value,
        video_service: videoService.value,
      })
      isConfigured.value = !!(llm.value.api_key && llm.value.base_url && modelToSave)
    } finally {
      isSaving.value = false
    }
  }

  // Reset to defaults
  function reset() {
    llm.value = { api_key: '', base_url: '', model: '' }
    comfyui.value = {
      comfyui_url: 'http://127.0.0.1:8188',
      comfyui_api_key: '',
      runninghub_api_key: '',
      runninghub_concurrent_limit: 1,
      runninghub_instance_type: '',
    }
    imageService.value = { provider: 'comfyui', api_key: '', base_url: '', model: '' }
    videoService.value = { provider: 'comfyui', api_key: '', base_url: '', model: '' }
    loadedModels.value = []
    customModel.value = ''
    selectedPreset.value = 'Custom'
    selectedImagePreset.value = ''
    selectedVideoPreset.value = ''
    isConfigured.value = false
  }

  return {
    // State
    llm,
    comfyui,
    imageService,
    videoService,
    llmPresets,
    imagePresets,
    videoPresets,
    selectedPreset,
    selectedImagePreset,
    selectedVideoPreset,
    loadedModels,
    customModel,
    isLoadingModels,
    isConfigured,
    isLoading,
    isSaving,
    isTesting,
    isTestingComfyUI,

    // Computed
    presetNames,
    currentModelSelection,
    currentApiKeyUrl,
    currentImageApiKeyUrl,
    currentVideoApiKeyUrl,
    currentPresetModels,
    currentImageModels,
    currentVideoModels,
    CUSTOM_MODEL_SENTINEL,

    // Actions
    loadConfig,
    loadPresets,
    loadImagePresets,
    loadVideoPresets,
    fetchModels,
    testConnection,
    testComfyUI,
    save,
    reset,
    applyPreset,
    applyImagePreset,
    applyVideoPreset,
    detectPreset,
    detectImagePreset,
    detectVideoPreset,
  }
})
