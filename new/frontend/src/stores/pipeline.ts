import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { PipelineType, VideoGenerateRequest, VideoMode } from '@/types'

export const usePipelineStore = defineStore('pipeline', () => {
  // Current pipeline
  const currentPipeline = ref<PipelineType>('quick_create')

  // Video generation parameters
  const text = ref('')
  const mode = ref<VideoMode>('generate')
  const title = ref('')
  const nScenes = ref(5)
  const ttsWorkflow = ref<string | null>(null)
  const refAudio = ref<string | null>(null)
  const voiceId = ref<string | null>(null)
  const mediaWorkflow = ref<string | null>(null)
  const frameTemplate = ref<string | null>(null)
  const templateParams = ref<Record<string, any> | null>(null)
  const promptPrefix = ref('')
  const bgmPath = ref<string | null>(null)
  const bgmVolume = ref(0.3)
  const videoFps = ref(30)

  // Generation state
  const isGenerating = ref(false)
  const currentTaskId = ref<string | null>(null)

  const buildRequest = (overrides: Partial<VideoGenerateRequest> = {}): VideoGenerateRequest => {
    const req: VideoGenerateRequest = {
      text: text.value,
      mode: mode.value,
      title: title.value || undefined,
      n_scenes: nScenes.value,
      video_fps: videoFps.value,
      bgm_volume: bgmVolume.value,
      pipeline: 'standard',
    }

    if (ttsWorkflow.value) req.tts_workflow = ttsWorkflow.value
    if (refAudio.value) req.ref_audio = refAudio.value
    if (voiceId.value) req.voice_id = voiceId.value
    if (mediaWorkflow.value) req.media_workflow = mediaWorkflow.value
    if (frameTemplate.value) req.frame_template = frameTemplate.value
    if (templateParams.value) req.template_params = templateParams.value
    if (promptPrefix.value) req.prompt_prefix = promptPrefix.value
    if (bgmPath.value) req.bgm_path = bgmPath.value

    return {
      ...req,
      ...overrides,
    }
  }

  const resetForm = () => {
    text.value = ''
    title.value = ''
    nScenes.value = 5
    promptPrefix.value = ''
    bgmPath.value = null
    bgmVolume.value = 0.3
    isGenerating.value = false
    currentTaskId.value = null
  }

  return {
    currentPipeline,
    text,
    mode,
    title,
    nScenes,
    ttsWorkflow,
    refAudio,
    voiceId,
    mediaWorkflow,
    frameTemplate,
    templateParams,
    promptPrefix,
    bgmPath,
    bgmVolume,
    videoFps,
    isGenerating,
    currentTaskId,
    buildRequest,
    resetForm,
  }
})
