<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import {
  VideoPlay,
  Star,
  Edit,
  Monitor,
  Film,
  Position,
  Document,
  Headset,
  Picture,
  Brush,
  VideoCamera,
  Mic,
  FolderOpened,
  CircleCheck,
  Upload,
  Delete,
  Plus,
} from '@element-plus/icons-vue'
import { usePipelineStore } from '@/stores/pipeline'
import { generateVideoAsync } from '@/api/video'
import { listTemplates, listMediaWorkflows, listTTSWorkflows, listBGM } from '@/api/resources'
import { uploadFile } from '@/api/upload'
import type { PipelineType, TemplateInfo, WorkflowInfo, BGMInfo, VideoGenerateRequest } from '@/types'

const { t } = useI18n()
const store = usePipelineStore()

// Pipeline icons mapping
const pipelineIcons: Record<string, any> = {
  quick_create: Star,
  custom_media: FolderOpened,
  digital_human: Monitor,
  image_to_video: Film,
  action_transfer: Position,
}

// Pipelines
const pipelines = computed(() => [
  { key: 'quick_create' as PipelineType, name: t('pipeline.quick_create.name'), desc: t('pipeline.quick_create.description') },
  { key: 'custom_media' as PipelineType, name: t('pipeline.custom_media.name'), desc: t('pipeline.custom_media.description') },
  { key: 'digital_human' as PipelineType, name: t('pipeline.digital_human.name'), desc: t('pipeline.digital_human.description') },
  { key: 'image_to_video' as PipelineType, name: t('pipeline.i2v.name'), desc: t('pipeline.i2v.description') },
  { key: 'action_transfer' as PipelineType, name: t('pipeline.action_transfer.name'), desc: t('pipeline.action_transfer.description') },
])

// Resources
const templates = ref<TemplateInfo[]>([])
const mediaWorkflows = ref<WorkflowInfo[]>([])
const ttsWorkflows = ref<WorkflowInfo[]>([])
const bgmFiles = ref<BGMInfo[]>([])
const resourcesLoading = ref(false)

const loadResources = async () => {
  resourcesLoading.value = true
  try {
    const [tmplRes, mediaRes, ttsRes, bgmRes] = await Promise.allSettled([
      listTemplates(),
      listMediaWorkflows(),
      listTTSWorkflows(),
      listBGM(),
    ])
    if (tmplRes.status === 'fulfilled') {
      templates.value = tmplRes.value.templates
      ensureDefaultTemplate()
    }
    if (mediaRes.status === 'fulfilled') mediaWorkflows.value = mediaRes.value.workflows
    if (ttsRes.status === 'fulfilled') ttsWorkflows.value = ttsRes.value.workflows
    if (bgmRes.status === 'fulfilled') bgmFiles.value = bgmRes.value.bgm_files
  } finally {
    resourcesLoading.value = false
  }
}

const ensureDefaultTemplate = () => {
  if (store.frameTemplate || templates.value.length === 0) return
  const preferred =
    templates.value.find((tmpl) => tmpl.key.includes('image_default.html')) ||
    templates.value.find((tmpl) => tmpl.key.includes('video_default.html')) ||
    templates.value[0]
  store.frameTemplate = preferred.key
}

// ============================================================
// Pipeline-specific state
// ============================================================

// quick_create
const splitMode = ref('paragraph')

// custom_media
const assetFiles = ref<{ name: string; path: string; url: string; type: string }[]>([])
const intent = ref('')
const duration = ref(30)

// digital_human
const characterFiles = ref<{ name: string; path: string; url: string }[]>([])
const productFiles = ref<{ name: string; path: string; url: string }[]>([])
const digitalMode = ref<'digital' | 'customize'>('digital')
const goodsTitle = ref('')

// i2v
const i2vImageFile = ref<{ name: string; path: string; url: string } | null>(null)

// action_transfer
const atVideoFile = ref<{ name: string; path: string; url: string } | null>(null)
const atImageFile = ref<{ name: string; path: string; url: string } | null>(null)

// TTS state
const ttsMode = ref<'local' | 'comfyui'>('local')
const ttsVoice = ref('zh-CN-YunjianNeural')
const ttsSpeed = ref(1.2)
const refAudioFile = ref<{ name: string; path: string; url: string } | null>(null)

// Voice options
const voiceOptions = [
  { id: 'zh-CN-YunjianNeural', label: 'voice.male_professional' },
  { id: 'zh-CN-YunxiNeural', label: 'voice.male_young' },
  { id: 'zh-CN-XiaoxiaoNeural', label: 'voice.female_gentle' },
  { id: 'zh-CN-XiaoyiNeural', label: 'voice.female_energetic' },
]

// Output state
const generatedVideoUrl = ref('')
const generatedDuration = ref(0)
const generatedFileSize = ref(0)
const generationTime = ref(0)

// ============================================================
// File upload helper
// ============================================================
const uploading = ref(false)

const handleFileUpload = async (file: File, target: 'asset' | 'character' | 'product' | 'i2v' | 'at_video' | 'at_image' | 'ref_audio') => {
  uploading.value = true
  try {
    const data = await uploadFile(file)
    const entry = {
      name: file.name,
      path: data.path,
      url: `/api/files/${data.path}`,
      type: file.type,
    }

    switch (target) {
      case 'asset':
        assetFiles.value.push(entry)
        break
      case 'character':
        characterFiles.value = [entry]
        break
      case 'product':
        productFiles.value = [entry]
        break
      case 'i2v':
        i2vImageFile.value = entry
        break
      case 'at_video':
        atVideoFile.value = entry
        break
      case 'at_image':
        atImageFile.value = entry
        break
      case 'ref_audio':
        refAudioFile.value = entry
        break
    }

    ElMessage.success(`Uploaded: ${file.name}`)
    return entry
  } catch (e: any) {
    ElMessage.error(`Upload failed: ${e.message}`)
    return null
  } finally {
    uploading.value = false
  }
}

const removeFile = (target: string, index?: number) => {
  switch (target) {
    case 'asset':
      if (index !== undefined) assetFiles.value.splice(index, 1)
      break
    case 'character':
      characterFiles.value = []
      break
    case 'product':
      productFiles.value = []
      break
    case 'i2v':
      i2vImageFile.value = null
      break
    case 'at_video':
      atVideoFile.value = null
      break
    case 'at_image':
      atImageFile.value = null
      break
    case 'ref_audio':
      refAudioFile.value = null
      break
  }
}

// ============================================================
// Video generation
// ============================================================
const isGenerating = computed(() => store.isGenerating)
const progressPercent = ref(0)
const progressMessage = ref('')
const generateStartTime = ref(0)

const inferWorkflowSource = () => {
  if (store.mediaWorkflow?.startsWith('selfhost/')) return 'selfhost'
  return 'runninghub'
}

const buildPipelineOverrides = (): Partial<VideoGenerateRequest> => {
  const ttsOverrides: Partial<VideoGenerateRequest> =
    ttsMode.value === 'local'
      ? {
          voice_id: ttsVoice.value,
          tts_speed: ttsSpeed.value,
          tts_workflow: undefined,
          ref_audio: undefined,
        }
      : {
          voice_id: undefined,
          tts_speed: undefined,
          tts_workflow: store.ttsWorkflow || undefined,
          ref_audio: refAudioFile.value?.path,
        }

  if (store.currentPipeline === 'custom_media') {
    const fallbackText =
      intent.value.trim() ||
      store.title.trim() ||
      assetFiles.value.map((file) => file.name).join(', ')

    return {
      ...ttsOverrides,
      pipeline: 'asset_based',
      text: fallbackText,
      title: store.title || undefined,
      video_title: store.title || undefined,
      intent: intent.value || undefined,
      duration: duration.value,
      source: inferWorkflowSource(),
      assets: assetFiles.value.map((file) => file.path),
    }
  }

  if (store.currentPipeline === 'digital_human') {
    return {
      ...ttsOverrides,
      pipeline: 'digital_human',
      digital_mode: digitalMode.value,
      character_assets: characterFiles.value.map((file) => file.path),
      goods_assets: productFiles.value.map((file) => file.path),
      goods_title: goodsTitle.value || undefined,
    }
  }

  if (store.currentPipeline === 'image_to_video') {
    return {
      ...ttsOverrides,
      pipeline: 'image_to_video',
      image: i2vImageFile.value?.path,
      prompt_text: store.text,
    }
  }

  if (store.currentPipeline === 'action_transfer') {
    return {
      ...ttsOverrides,
      pipeline: 'action_transfer',
      action_video: atVideoFile.value?.path,
      action_image: atImageFile.value?.path,
      prompt_text: store.text,
    }
  }

  return {
    ...ttsOverrides,
    pipeline: 'standard',
  }
}

const handleGenerate = async () => {
  // Validate based on pipeline
  if (store.currentPipeline === 'quick_create') {
    if (!store.text.trim()) {
      ElMessage.error(t('error.input_required'))
      return
    }
    if (!store.frameTemplate) {
      ElMessage.error(t('template.select'))
      return
    }
  } else if (store.currentPipeline === 'custom_media') {
    if (assetFiles.value.length === 0) {
      ElMessage.error(t('asset_based.empty_hint'))
      return
    }
  } else if (store.currentPipeline === 'digital_human') {
    if (characterFiles.value.length === 0) {
      ElMessage.error(t('digital_human.character_empty_hint'))
      return
    }
  } else if (store.currentPipeline === 'image_to_video') {
    if (!i2vImageFile.value) {
      ElMessage.error(t('i2v.character_empty_hint'))
      return
    }
  } else if (store.currentPipeline === 'action_transfer') {
    if (!atVideoFile.value) {
      ElMessage.error(t('action_transfer.video_empty_hint'))
      return
    }
    if (!atImageFile.value) {
      ElMessage.error(t('action_transfer.image_empty_hint'))
      return
    }
  }

  if (
    store.currentPipeline === 'digital_human' ||
    store.currentPipeline === 'image_to_video' ||
    store.currentPipeline === 'action_transfer'
  ) {
    ElMessage.error('当前后端暂未开放该流程的 API，请先使用快速创建或自定义素材流程')
    return
  }

  store.isGenerating = true
  progressPercent.value = 0
  progressMessage.value = t('status.initializing')
  generateStartTime.value = Date.now()
  generatedVideoUrl.value = ''

  try {
    const req = store.buildRequest(buildPipelineOverrides())
    const data = await generateVideoAsync(req)
    store.currentTaskId = data.task_id

    ElMessage.success(t('status.generating'))

    // Poll task progress
    const pollInterval = setInterval(async () => {
      try {
        const { getTaskStatus } = await import('@/api/tasks')
        const task = await getTaskStatus(data.task_id)

        if (task.progress) {
          progressPercent.value = task.progress.percentage
          progressMessage.value = task.progress.message || ''
        }

        if (task.status === 'completed') {
          clearInterval(pollInterval)
          store.isGenerating = false
          generationTime.value = Math.round((Date.now() - generateStartTime.value) / 1000)
          ElMessage.success(t('status.success'))
          if (task.result?.video_url) {
            generatedVideoUrl.value = task.result.video_url
            generatedDuration.value = task.result.duration || 0
            generatedFileSize.value = task.result.file_size || 0
            progressMessage.value = ''
          }
        } else if (task.status === 'failed') {
          clearInterval(pollInterval)
          store.isGenerating = false
          ElMessage.error(t('status.error', { error: task.error || 'Unknown error' }))
        }
      } catch {
        clearInterval(pollInterval)
        store.isGenerating = false
      }
    }, 3000)
  } catch {
    store.isGenerating = false
  }
}

onMounted(() => {
  loadResources()
})

const openUrl = (url: string) => {
  window.open(url, '_blank')
}
</script>

<template>
  <div class="home-view animate-fade-in">
    <!-- Hero Section -->
    <div class="hero-section">
      <h1 class="hero-title">{{ t('progressive.pipeline.title') }}</h1>
      <p class="hero-subtitle">{{ t('progressive.pipeline.caption') }}</p>
    </div>

    <!-- Pipeline Selection -->
    <div class="pipeline-section">
      <div class="pipeline-grid">
        <div
          v-for="p in pipelines"
          :key="p.key"
          class="pipeline-card"
          :class="{ active: store.currentPipeline === p.key }"
          @click="store.currentPipeline = p.key"
        >
          <div class="pipeline-card-icon">
            <el-icon :size="28"><component :is="pipelineIcons[p.key]" /></el-icon>
          </div>
          <div class="pipeline-card-content">
            <h3 class="pipeline-card-name">{{ p.name }}</h3>
            <p class="pipeline-card-desc">{{ p.desc }}</p>
          </div>
          <div class="pipeline-card-check" v-if="store.currentPipeline === p.key">
            <el-icon><CircleCheck /></el-icon>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="content-area">
      <!-- Left: Pipeline-Specific Input Section -->
      <div class="input-section">

        <!-- ========================================== -->
        <!-- quick_create: Content Input -->
        <!-- ========================================== -->
        <template v-if="store.currentPipeline === 'quick_create'">
          <div class="section-card">
            <div class="section-card-header">
              <el-icon class="section-icon"><Edit /></el-icon>
              <span>{{ t('section.content_input') }}</span>
            </div>
            <div class="section-card-body">
              <!-- Mode Selection -->
              <div class="mode-selector">
                <button class="mode-btn" :class="{ active: store.mode === 'generate' }" @click="store.mode = 'generate'">
                  <el-icon><Star /></el-icon>
                  <span>{{ t('mode.generate') }}</span>
                </button>
                <button class="mode-btn" :class="{ active: store.mode === 'fixed' }" @click="store.mode = 'fixed'">
                  <el-icon><Edit /></el-icon>
                  <span>{{ t('mode.fixed') }}</span>
                </button>
              </div>

              <!-- Text Input -->
              <div class="input-group">
                <label class="input-label">
                  {{ store.mode === 'generate' ? t('input.topic') : t('input.content') }}
                </label>
                <el-input
                  v-model="store.text"
                  type="textarea"
                  :rows="store.mode === 'generate' ? 4 : 6"
                  :placeholder="store.mode === 'generate' ? t('input.topic_placeholder') : t('input.content_placeholder')"
                  class="content-textarea"
                />
              </div>

              <!-- Split Mode (fixed mode only) -->
              <div v-if="store.mode === 'fixed'" class="input-group">
                <label class="input-label">{{ t('split.mode_label') }}</label>
                <el-select v-model="splitMode" class="full-select">
                  <el-option :label="t('split.mode_paragraph')" value="paragraph" />
                  <el-option :label="t('split.mode_line')" value="line" />
                  <el-option :label="t('split.mode_sentence')" value="sentence" />
                </el-select>
              </div>

              <!-- Title & Scenes -->
              <div class="input-row">
                <div class="input-group flex-1">
                  <label class="input-label">{{ t('input.title') }}</label>
                  <el-input v-model="store.title" :placeholder="t('input.title_placeholder')" />
                </div>
                <div class="input-group scenes-group" v-if="store.mode === 'generate'">
                  <label class="input-label">{{ t('video.frames') }}</label>
                  <div class="scenes-control">
                    <el-slider v-model="store.nScenes" :min="3" :max="30" :show-tooltip="false" />
                    <span class="scenes-value">{{ store.nScenes }}</span>
                  </div>
                </div>
              </div>
              <p v-if="store.mode === 'fixed'" class="hint-text">
                {{ t('video.frames_fixed_mode_hint') }}
              </p>
            </div>
          </div>
        </template>

        <!-- ========================================== -->
        <!-- custom_media: Asset Upload -->
        <!-- ========================================== -->
        <template v-if="store.currentPipeline === 'custom_media'">
          <div class="section-card">
            <div class="section-card-header">
              <el-icon class="section-icon"><Upload /></el-icon>
              <span>{{ t('asset_based.section_assets') }}</span>
            </div>
            <div class="section-card-body">
              <p class="section-desc">{{ t('asset_based.assets_what') }}</p>

              <!-- Upload Area -->
              <el-upload
                class="asset-upload-area"
                drag
                multiple
                :auto-upload="false"
                :on-change="(file: any) => handleFileUpload(file.raw, 'asset')"
                accept=".jpg,.jpeg,.png,.gif,.webp,.mp4,.mov,.avi,.mkv,.webm"
              >
                <el-icon :size="40"><Upload /></el-icon>
                <div class="el-upload__text">{{ t('asset_based.upload') }}</div>
                <template #tip>
                  <div class="el-upload__tip">{{ t('asset_based.upload_help') }}</div>
                </template>
              </el-upload>

              <!-- Asset Preview Grid -->
              <div v-if="assetFiles.length > 0" class="asset-preview-grid">
                <div v-for="(file, idx) in assetFiles" :key="idx" class="asset-preview-item">
                  <img v-if="file.type.startsWith('image')" :src="file.url" :alt="file.name" />
                  <video v-else :src="file.url" />
                  <el-button
                    class="asset-remove-btn"
                    :icon="Delete"
                    circle
                    size="small"
                    type="danger"
                    @click="removeFile('asset', idx)"
                  />
                  <span class="asset-name">{{ file.name }}</span>
                </div>
              </div>
              <p v-else class="hint-text">{{ t('asset_based.empty_hint') }}</p>
            </div>
          </div>

          <!-- Video Info -->
          <div class="section-card">
            <div class="section-card-header">
              <el-icon class="section-icon"><Document /></el-icon>
              <span>{{ t('asset_based.section_video_info') }}</span>
            </div>
            <div class="section-card-body">
              <div class="input-group">
                <label class="input-label">{{ t('asset_based.video_title') }}</label>
                <el-input v-model="store.title" :placeholder="t('asset_based.video_title_placeholder')" />
              </div>
              <div class="input-group">
                <label class="input-label">{{ t('asset_based.intent') }}</label>
                <el-input v-model="intent" type="textarea" :rows="3" :placeholder="t('asset_based.intent_placeholder')" />
              </div>
              <div class="input-group">
                <label class="input-label">{{ t('asset_based.duration') }}: {{ duration }}s</label>
                <el-slider v-model="duration" :min="15" :max="120" :step="5" show-stops />
              </div>
            </div>
          </div>
        </template>

        <!-- ========================================== -->
        <!-- digital_human: Character & Product -->
        <!-- ========================================== -->
        <template v-if="store.currentPipeline === 'digital_human'">
          <!-- Character Upload -->
          <div class="section-card">
            <div class="section-card-header">
              <el-icon class="section-icon"><Upload /></el-icon>
              <span>{{ t('digital_human.section_character_assets') }}</span>
            </div>
            <div class="section-card-body">
              <p class="section-desc">{{ t('digital_human.character_what') }}</p>
              <el-upload
                class="asset-upload-area"
                drag
                :auto-upload="false"
                :on-change="(file: any) => handleFileUpload(file.raw, 'character')"
                accept=".jpg,.jpeg,.png,.webp"
                :limit="1"
              >
                <el-icon :size="40"><Upload /></el-icon>
                <div class="el-upload__text">{{ t('digital_human.upload') }}</div>
              </el-upload>
              <div v-if="characterFiles.length > 0" class="asset-preview-grid single">
                <div class="asset-preview-item">
                  <img :src="characterFiles[0].url" alt="character" />
                  <el-button class="asset-remove-btn" :icon="Delete" circle size="small" type="danger" @click="removeFile('character')" />
                </div>
              </div>
              <p v-else class="hint-text">{{ t('digital_human.character_empty_hint') }}</p>
            </div>
          </div>

          <!-- Mode Selection -->
          <div class="section-card">
            <div class="section-card-header">
              <el-icon class="section-icon"><Star /></el-icon>
              <span>{{ t('digital_human.section_select_mode') }}</span>
            </div>
            <div class="section-card-body">
              <div class="mode-selector">
                <button class="mode-btn" :class="{ active: digitalMode === 'digital' }" @click="digitalMode = 'digital'">
                  <el-icon><Star /></el-icon>
                  <span>{{ t('mode.digital') }}</span>
                </button>
                <button class="mode-btn" :class="{ active: digitalMode === 'customize' }" @click="digitalMode = 'customize'">
                  <el-icon><Edit /></el-icon>
                  <span>{{ t('mode.customize') }}</span>
                </button>
              </div>

              <!-- Digital mode: Product upload + goods title -->
              <template v-if="digitalMode === 'digital'">
                <div class="input-group">
                  <label class="input-label">{{ t('digital_human.section_goods_info') }}</label>
                  <el-upload
                    class="asset-upload-area small"
                    drag
                    :auto-upload="false"
                    :on-change="(file: any) => handleFileUpload(file.raw, 'product')"
                    accept=".jpg,.jpeg,.png,.webp"
                    :limit="1"
                  >
                    <el-icon :size="32"><Upload /></el-icon>
                    <div class="el-upload__text">{{ t('digital_human.upload') }}</div>
                  </el-upload>
                  <div v-if="productFiles.length > 0" class="asset-preview-grid single small">
                    <div class="asset-preview-item">
                      <img :src="productFiles[0].url" alt="product" />
                      <el-button class="asset-remove-btn" :icon="Delete" circle size="small" type="danger" @click="removeFile('product')" />
                    </div>
                  </div>
                  <p v-else class="hint-text">{{ t('digital_human.goods_empty_hint') }}</p>
                </div>
                <div class="input-group">
                  <label class="input-label">{{ t('digital_human.goods_title') }}</label>
                  <el-input v-model="goodsTitle" :placeholder="t('digital_human.goods_title_placeholder')" />
                </div>
                <div class="input-group">
                  <label class="input-label">{{ t('digital_human.input_text') }}</label>
                  <el-input v-model="store.text" type="textarea" :rows="4" :placeholder="t('digital_human.digital_mode')" />
                </div>
              </template>

              <!-- Customize mode: text input -->
              <template v-if="digitalMode === 'customize'">
                <div class="input-group">
                  <label class="input-label">{{ t('digital_human.customize_text') }}</label>
                  <el-input v-model="store.text" type="textarea" :rows="6" :placeholder="t('digital_human.customize_mode')" />
                </div>
              </template>
            </div>
          </div>
        </template>

        <!-- ========================================== -->
        <!-- image_to_video: Image + Prompt -->
        <!-- ========================================== -->
        <template v-if="store.currentPipeline === 'image_to_video'">
          <div class="section-card">
            <div class="section-card-header">
              <el-icon class="section-icon"><Upload /></el-icon>
              <span>{{ t('i2v.video_generation') }}</span>
            </div>
            <div class="section-card-body">
              <p class="section-desc">{{ t('i2v.image_what') }}</p>
              <el-upload
                class="asset-upload-area"
                drag
                :auto-upload="false"
                :on-change="(file: any) => handleFileUpload(file.raw, 'i2v')"
                accept=".jpg,.jpeg,.png,.webp"
                :limit="1"
              >
                <el-icon :size="40"><Upload /></el-icon>
                <div class="el-upload__text">{{ t('i2v.upload') }}</div>
              </el-upload>
              <div v-if="i2vImageFile" class="asset-preview-grid single">
                <div class="asset-preview-item">
                  <img :src="i2vImageFile.url" alt="i2v" />
                  <el-button class="asset-remove-btn" :icon="Delete" circle size="small" type="danger" @click="removeFile('i2v')" />
                </div>
              </div>
              <p v-else class="hint-text">{{ t('i2v.character_empty_hint') }}</p>

              <div class="input-group mt-4">
                <label class="input-label">{{ t('i2v.input_text') }}</label>
                <el-input v-model="store.text" type="textarea" :rows="4" :placeholder="t('i2v.input_text')" />
              </div>
            </div>
          </div>
        </template>

        <!-- ========================================== -->
        <!-- action_transfer: Video + Image + Prompt -->
        <!-- ========================================== -->
        <template v-if="store.currentPipeline === 'action_transfer'">
          <!-- Video Upload -->
          <div class="section-card">
            <div class="section-card-header">
              <el-icon class="section-icon"><Film /></el-icon>
              <span>{{ t('action_transfer.video_upload') }}</span>
            </div>
            <div class="section-card-body">
              <p class="section-desc">{{ t('action_transfer.video_what') }}</p>
              <el-upload
                class="asset-upload-area"
                drag
                :auto-upload="false"
                :on-change="(file: any) => handleFileUpload(file.raw, 'at_video')"
                accept=".mp4,.mkv,.mov"
                :limit="1"
              >
                <el-icon :size="40"><Upload /></el-icon>
                <div class="el-upload__text">{{ t('action_transfer.video_upload') }}</div>
                <template #tip>
                  <div class="el-upload__tip">{{ t('action_transfer.video_upload_help') }}</div>
                </template>
              </el-upload>
              <div v-if="atVideoFile" class="asset-preview-grid single">
                <div class="asset-preview-item">
                  <video :src="atVideoFile.url" controls />
                  <el-button class="asset-remove-btn" :icon="Delete" circle size="small" type="danger" @click="removeFile('at_video')" />
                </div>
              </div>
              <p v-else class="hint-text">{{ t('action_transfer.video_empty_hint') }}</p>
            </div>
          </div>

          <!-- Image Upload -->
          <div class="section-card">
            <div class="section-card-header">
              <el-icon class="section-icon"><Picture /></el-icon>
              <span>{{ t('action_transfer.image_upload') }}</span>
            </div>
            <div class="section-card-body">
              <p class="section-desc">{{ t('action_transfer.image_what') }}</p>
              <el-upload
                class="asset-upload-area"
                drag
                :auto-upload="false"
                :on-change="(file: any) => handleFileUpload(file.raw, 'at_image')"
                accept=".jpg,.jpeg,.png,.webp"
                :limit="1"
              >
                <el-icon :size="40"><Upload /></el-icon>
                <div class="el-upload__text">{{ t('action_transfer.image_upload') }}</div>
              </el-upload>
              <div v-if="atImageFile" class="asset-preview-grid single">
                <div class="asset-preview-item">
                  <img :src="atImageFile.url" alt="action transfer" />
                  <el-button class="asset-remove-btn" :icon="Delete" circle size="small" type="danger" @click="removeFile('at_image')" />
                </div>
              </div>
              <p v-else class="hint-text">{{ t('action_transfer.image_empty_hint') }}</p>

              <div class="input-group mt-4">
                <label class="input-label">{{ t('action_transfer.input_text') }}</label>
                <el-input v-model="store.text" type="textarea" :rows="3" :placeholder="t('action_transfer.input_text')" />
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- Right: Common Settings Section -->
      <div class="settings-section">
        <!-- TTS Configuration -->
        <div class="section-card">
          <div class="section-card-header">
            <el-icon class="section-icon"><Mic /></el-icon>
            <span>{{ t('section.tts') }}</span>
          </div>
          <div class="section-card-body">
            <!-- TTS Mode Toggle -->
            <div class="mode-selector small">
              <button class="mode-btn" :class="{ active: ttsMode === 'local' }" @click="ttsMode = 'local'">
                {{ t('tts.mode.local') }}
              </button>
              <button class="mode-btn" :class="{ active: ttsMode === 'comfyui' }" @click="ttsMode = 'comfyui'">
                {{ t('tts.mode.comfyui') }}
              </button>
            </div>

            <!-- Local Mode: Voice + Speed -->
            <template v-if="ttsMode === 'local'">
              <div class="input-group">
                <label class="input-label">{{ t('tts.voice_selector') }}</label>
                <el-select v-model="ttsVoice" class="full-select">
                  <el-option
                    v-for="v in voiceOptions"
                    :key="v.id"
                    :label="t(v.label)"
                    :value="v.id"
                  />
                </el-select>
              </div>
              <div class="input-group">
                <label class="input-label">{{ t('tts.speed') }}: {{ ttsSpeed.toFixed(1) }}x</label>
                <el-slider v-model="ttsSpeed" :min="0.5" :max="2.0" :step="0.1" />
              </div>
            </template>

            <!-- ComfyUI Mode: Workflow + Ref Audio -->
            <template v-if="ttsMode === 'comfyui'">
              <div class="input-group">
                <label class="input-label">{{ t('tts.selector') }}</label>
                <el-select v-model="store.ttsWorkflow" class="full-select" clearable>
                  <el-option
                    v-for="wf in ttsWorkflows"
                    :key="wf.key"
                    :label="wf.display_name"
                    :value="wf.key"
                  />
                </el-select>
              </div>
              <div class="input-group">
                <label class="input-label">{{ t('tts.ref_audio') }}</label>
                <el-upload
                  class="ref-audio-upload"
                  :auto-upload="false"
                  :on-change="(file: any) => handleFileUpload(file.raw, 'ref_audio')"
                  accept=".mp3,.wav,.flac,.m4a,.aac,.ogg"
                  :limit="1"
                  :show-file-list="false"
                >
                  <el-button size="small" :icon="Upload">{{ t('tts.ref_audio') }}</el-button>
                </el-upload>
                <div v-if="refAudioFile" class="ref-audio-preview">
                  <audio :src="refAudioFile.url" controls class="audio-player" />
                  <el-button :icon="Delete" circle size="small" type="danger" @click="removeFile('ref_audio')" />
                </div>
                <p v-else class="hint-text small">{{ t('tts.ref_audio_help') }}</p>
              </div>
            </template>
          </div>
        </div>

        <!-- Template Card (quick_create only) -->
        <div class="section-card" v-if="store.currentPipeline === 'quick_create'">
          <div class="section-card-header">
            <el-icon class="section-icon"><Picture /></el-icon>
            <span>{{ t('template.selector') }}</span>
          </div>
          <div class="section-card-body">
            <el-select v-model="store.frameTemplate" :placeholder="t('template.select')" class="full-select" filterable>
              <el-option
                v-for="tmpl in templates"
                :key="tmpl.key"
                :label="`${tmpl.name} (${tmpl.width}x${tmpl.height})`"
                :value="tmpl.key"
              />
            </el-select>
          </div>
        </div>

        <!-- Media Workflow Card -->
        <div class="section-card">
          <div class="section-card-header">
            <el-icon class="section-icon"><Brush /></el-icon>
            <span>{{ t('style.workflow') }}</span>
          </div>
          <div class="section-card-body">
            <div class="workflow-group" v-if="store.currentPipeline !== 'quick_create'">
              <label class="input-label">
                <el-icon><Mic /></el-icon>
                {{ t('tts.selector') }}
              </label>
              <el-select v-model="store.ttsWorkflow" :placeholder="t('tts.selector')" class="full-select" clearable>
                <el-option v-for="wf in ttsWorkflows" :key="wf.key" :label="wf.display_name" :value="wf.key" />
              </el-select>
            </div>

            <div class="workflow-group" v-if="store.currentPipeline !== 'action_transfer'">
              <label class="input-label">
                <el-icon><VideoCamera /></el-icon>
                {{ store.currentPipeline === 'image_to_video' ? t('i2v.workflow_select') : t('style.workflow') }}
              </label>
              <el-select v-model="store.mediaWorkflow" :placeholder="t('style.workflow')" class="full-select" clearable>
                <el-option v-for="wf in mediaWorkflows" :key="wf.key" :label="wf.display_name" :value="wf.key" />
              </el-select>
            </div>
            <div class="workflow-group" v-else>
              <label class="input-label">
                <el-icon><VideoCamera /></el-icon>
                {{ t('action_transfer.workflow_select') }}
              </label>
              <el-select v-model="store.mediaWorkflow" :placeholder="t('action_transfer.workflow_select')" class="full-select" clearable>
                <el-option v-for="wf in mediaWorkflows" :key="wf.key" :label="wf.display_name" :value="wf.key" />
              </el-select>
            </div>
          </div>
        </div>

        <!-- BGM Card -->
        <div class="section-card">
          <div class="section-card-header">
            <el-icon class="section-icon"><Headset /></el-icon>
            <span>{{ t('section.bgm') }}</span>
          </div>
          <div class="section-card-body">
            <el-select v-model="store.bgmPath" :placeholder="t('bgm.selector')" class="full-select" clearable>
              <el-option :label="t('bgm.none')" :value="''" />
              <el-option v-for="bgm in bgmFiles" :key="bgm.path" :label="bgm.name" :value="bgm.path" />
            </el-select>
            <div class="volume-control" v-if="store.bgmPath">
              <label class="input-label">{{ t('bgm.volume') }}: {{ Math.round(store.bgmVolume * 100) }}%</label>
              <el-slider v-model="store.bgmVolume" :min="0" :max="0.5" :step="0.01" />
            </div>
          </div>
        </div>

        <!-- Prompt Prefix (quick_create, custom_media) -->
        <div class="section-card" v-if="store.currentPipeline === 'quick_create' || store.currentPipeline === 'custom_media'">
          <div class="section-card-header">
            <el-icon class="section-icon"><Document /></el-icon>
            <span>{{ t('style.prompt_prefix') }}</span>
          </div>
          <div class="section-card-body">
            <el-input v-model="store.promptPrefix" :placeholder="t('style.prompt_prefix_placeholder')" />
            <p class="hint-text small mt-2">{{ t('style.prompt_prefix_help') }}</p>
          </div>
        </div>

        <!-- Generate Button -->
        <div class="generate-section">
          <el-button
            type="primary"
            size="large"
            class="generate-btn"
            :loading="isGenerating"
            @click="handleGenerate"
          >
            <template v-if="!isGenerating">
              <el-icon><VideoPlay /></el-icon>
              <span>{{ t('btn.generate') }}</span>
            </template>
            <template v-else>
              <span>{{ progressMessage || t('status.generating') }}</span>
            </template>
          </el-button>

          <!-- Progress -->
          <transition name="slide-fade">
            <div v-if="isGenerating" class="progress-container">
              <el-progress :percentage="progressPercent" :stroke-width="10" :show-text="false" class="generate-progress" />
              <span class="progress-text">{{ Math.round(progressPercent) }}%</span>
            </div>
          </transition>
        </div>

        <!-- Output Preview -->
        <transition name="slide-fade">
          <div v-if="generatedVideoUrl" class="section-card output-card">
            <div class="section-card-header">
              <el-icon class="section-icon"><VideoCamera /></el-icon>
              <span>{{ t('info.video_information') }}</span>
            </div>
            <div class="section-card-body">
              <video :src="generatedVideoUrl" controls class="output-video" />
              <div class="output-info">
                <div class="info-row" v-if="generationTime">
                  <span class="info-label">{{ t('info.generation_time') }}</span>
                  <span class="info-value">{{ generationTime }}s</span>
                </div>
                <div class="info-row" v-if="generatedDuration">
                  <span class="info-label">{{ t('info.duration') }}</span>
                  <span class="info-value">{{ Math.round(generatedDuration) }}s</span>
                </div>
                <div class="info-row" v-if="generatedFileSize">
                  <span class="info-label">{{ t('info.file_size') }}</span>
                  <span class="info-value">{{ (generatedFileSize / 1024 / 1024).toFixed(1) }}MB</span>
                </div>
              </div>
              <el-button type="primary" class="download-btn" @click="openUrl(generatedVideoUrl)">
                {{ t('history.task_card.download') }}
              </el-button>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-view {
  padding-bottom: var(--pv-space-10);
}

/* Hero Section */
.hero-section {
  text-align: center;
  margin-bottom: var(--pv-space-8);
  padding: var(--pv-space-8) 0 var(--pv-space-4);
}

.hero-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--pv-text);
  margin-bottom: var(--pv-space-2);
  letter-spacing: -0.5px;
}

.hero-subtitle {
  font-size: 16px;
  color: var(--pv-text-secondary);
  max-width: 500px;
  margin: 0 auto;
}

/* Pipeline Grid */
.pipeline-section {
  margin-bottom: var(--pv-space-6);
}

.pipeline-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: var(--pv-space-4);
}

@media (max-width: 1200px) {
  .pipeline-grid { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 768px) {
  .pipeline-grid { grid-template-columns: repeat(2, 1fr); }
}

.pipeline-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--pv-space-6) var(--pv-space-4);
  background: var(--pv-surface);
  border: 2px solid var(--pv-border-light);
  border-radius: var(--pv-radius-xl);
  cursor: pointer;
  transition: all var(--pv-transition);
  text-align: center;
}

.pipeline-card:hover {
  border-color: var(--pv-primary-200);
  background: var(--pv-primary-50);
  transform: translateY(-2px);
  box-shadow: var(--pv-shadow-lg);
}

.pipeline-card.active {
  border-color: var(--pv-primary);
  background: linear-gradient(135deg, var(--pv-primary-50), var(--pv-primary-100));
  box-shadow: 0 4px 20px rgb(99 102 241 / 0.2);
}

.pipeline-card-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--pv-primary-100), var(--pv-primary-200));
  border-radius: var(--pv-radius-lg);
  margin-bottom: var(--pv-space-3);
  color: var(--pv-primary);
  transition: all var(--pv-transition);
}

.pipeline-card:hover .pipeline-card-icon { transform: scale(1.1); }

.pipeline-card.active .pipeline-card-icon {
  background: linear-gradient(135deg, var(--pv-primary), var(--pv-primary-dark));
  color: white;
  box-shadow: 0 4px 12px rgb(99 102 241 / 0.4);
}

.pipeline-card-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--pv-text);
  margin-bottom: var(--pv-space-1);
}

.pipeline-card-desc {
  font-size: 12px;
  color: var(--pv-text-secondary);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.pipeline-card-check {
  position: absolute;
  top: var(--pv-space-2);
  right: var(--pv-space-2);
  color: var(--pv-primary);
  font-size: 20px;
}

/* Content Area Layout */
.content-area {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: var(--pv-space-6);
}

@media (max-width: 1024px) {
  .content-area { grid-template-columns: 1fr; }
}

/* Section Cards */
.section-card {
  background: var(--pv-surface);
  border: 1px solid var(--pv-border-light);
  border-radius: var(--pv-radius-lg);
  overflow: hidden;
  margin-bottom: var(--pv-space-4);
  transition: all var(--pv-transition);
}

.section-card:hover {
  box-shadow: var(--pv-shadow-md);
  border-color: var(--pv-border);
}

.section-card-header {
  display: flex;
  align-items: center;
  gap: var(--pv-space-2);
  padding: var(--pv-space-4) var(--pv-space-5);
  background: linear-gradient(to bottom, var(--pv-surface), var(--pv-bg));
  border-bottom: 1px solid var(--pv-border-light);
  font-weight: 600;
  font-size: 15px;
  color: var(--pv-text);
}

.section-icon {
  color: var(--pv-primary);
  font-size: 18px;
}

.section-card-body {
  padding: var(--pv-space-5);
}

.section-desc {
  font-size: 13px;
  color: var(--pv-text-secondary);
  margin-bottom: var(--pv-space-4);
  line-height: 1.5;
}

/* Mode Selector */
.mode-selector {
  display: flex;
  gap: var(--pv-space-2);
  padding: var(--pv-space-1);
  background: var(--pv-bg);
  border-radius: var(--pv-radius);
  margin-bottom: var(--pv-space-5);
}

.mode-selector.small {
  margin-bottom: var(--pv-space-4);
}

.mode-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--pv-space-2);
  padding: var(--pv-space-3) var(--pv-space-4);
  border: none;
  border-radius: var(--pv-radius-sm);
  background: transparent;
  color: var(--pv-text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--pv-transition);
}

.mode-btn:hover {
  color: var(--pv-text);
  background: var(--pv-surface);
}

.mode-btn.active {
  color: var(--pv-primary);
  background: var(--pv-surface);
  box-shadow: var(--pv-shadow-sm);
}

/* Input Groups */
.input-group {
  margin-bottom: var(--pv-space-4);
}

.input-label {
  display: flex;
  align-items: center;
  gap: var(--pv-space-1);
  font-size: 13px;
  font-weight: 500;
  color: var(--pv-text-secondary);
  margin-bottom: var(--pv-space-2);
}

.content-textarea :deep(.el-textarea__inner) {
  resize: vertical;
  min-height: 120px;
}

.input-row {
  display: flex;
  gap: var(--pv-space-4);
}

.flex-1 { flex: 1; }

.scenes-group { width: 200px; }

.scenes-control {
  display: flex;
  align-items: center;
  gap: var(--pv-space-3);
}

.scenes-value {
  min-width: 32px;
  text-align: center;
  font-weight: 600;
  font-size: 16px;
  color: var(--pv-primary);
}

.full-select { width: 100%; }

/* Workflow Groups */
.workflow-group {
  margin-bottom: var(--pv-space-4);
}

.workflow-group:last-child { margin-bottom: 0; }

.workflow-group .input-label .el-icon { font-size: 14px; }

/* BGM */
.volume-control {
  margin-top: var(--pv-space-4);
}

.volume-control .el-slider {
  margin-top: var(--pv-space-2);
}

/* Asset Upload */
.asset-upload-area {
  width: 100%;
}

.asset-upload-area.small :deep(.el-upload-dragger) {
  padding: var(--pv-space-4);
}

.asset-preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: var(--pv-space-3);
  margin-top: var(--pv-space-4);
}

.asset-preview-grid.single {
  grid-template-columns: 200px;
}

.asset-preview-grid.small {
  grid-template-columns: 140px;
}

.asset-preview-item {
  position: relative;
  border-radius: var(--pv-radius);
  overflow: hidden;
  border: 1px solid var(--pv-border-light);
}

.asset-preview-item img,
.asset-preview-item video {
  width: 100%;
  height: 120px;
  object-fit: cover;
  display: block;
}

.asset-remove-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  opacity: 0;
  transition: opacity var(--pv-transition);
}

.asset-preview-item:hover .asset-remove-btn { opacity: 1; }

.asset-name {
  display: block;
  font-size: 11px;
  color: var(--pv-text-secondary);
  padding: 4px 6px;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}

/* Ref Audio */
.ref-audio-preview {
  display: flex;
  align-items: center;
  gap: var(--pv-space-3);
  margin-top: var(--pv-space-3);
}

.audio-player {
  flex: 1;
  height: 36px;
}

/* Hints */
.hint-text {
  font-size: 12px;
  color: var(--pv-text-muted);
  margin-top: var(--pv-space-2);
}

.hint-text.small {
  font-size: 11px;
  margin-top: var(--pv-space-1);
}

.mt-2 { margin-top: var(--pv-space-2); }
.mt-4 { margin-top: var(--pv-space-4); }

/* Generate Section */
.generate-section {
  margin-top: var(--pv-space-4);
}

.generate-btn {
  width: 100%;
  height: 52px;
  font-size: 16px;
  font-weight: 600;
  border-radius: var(--pv-radius-lg);
  background: linear-gradient(135deg, var(--pv-primary), #7c3aed);
  border: none;
  box-shadow: 0 4px 16px rgb(99 102 241 / 0.3);
  transition: all var(--pv-transition);
}

.generate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgb(99 102 241 / 0.4);
}

.generate-btn:active { transform: translateY(0); }

.generate-btn .el-icon { margin-right: var(--pv-space-2); }

.progress-container {
  display: flex;
  align-items: center;
  gap: var(--pv-space-3);
  margin-top: var(--pv-space-4);
}

.generate-progress { flex: 1; }

.generate-progress :deep(.el-progress-bar__inner) {
  background: linear-gradient(90deg, var(--pv-primary-light), #7c3aed);
}

.progress-text {
  font-weight: 600;
  font-size: 14px;
  color: var(--pv-primary);
  min-width: 40px;
}

/* Output Card */
.output-card {
  border-color: var(--pv-primary-200);
  background: var(--pv-primary-50);
}

.output-video {
  width: 100%;
  max-height: 360px;
  border-radius: var(--pv-radius);
  background: #000;
  margin-bottom: var(--pv-space-4);
}

.output-info {
  display: flex;
  flex-direction: column;
  gap: var(--pv-space-2);
  margin-bottom: var(--pv-space-4);
}

.info-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.info-label { color: var(--pv-text-secondary); }
.info-value { font-weight: 600; color: var(--pv-text); }

.download-btn { width: 100%; }

/* Transitions */
.slide-fade-enter-active { transition: all 0.3s ease-out; }
.slide-fade-leave-active { transition: all 0.2s ease-in; }
.slide-fade-enter-from { transform: translateY(-10px); opacity: 0; }
.slide-fade-leave-to { transform: translateY(-10px); opacity: 0; }
</style>
