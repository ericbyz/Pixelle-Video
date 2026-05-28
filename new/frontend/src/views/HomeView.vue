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
} from '@element-plus/icons-vue'
import { usePipelineStore } from '@/stores/pipeline'
import { generateVideoAsync } from '@/api/video'
import { listTemplates, listMediaWorkflows, listTTSWorkflows, listBGM } from '@/api/resources'
import type { PipelineType, TemplateInfo, WorkflowInfo, BGMInfo } from '@/types'

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
    if (tmplRes.status === 'fulfilled') templates.value = tmplRes.value.data.templates
    if (mediaRes.status === 'fulfilled') mediaWorkflows.value = mediaRes.value.data.workflows
    if (ttsRes.status === 'fulfilled') ttsWorkflows.value = ttsRes.value.data.workflows
    if (bgmRes.status === 'fulfilled') bgmFiles.value = bgmRes.value.data.bgm_files
  } finally {
    resourcesLoading.value = false
  }
}

// Video generation
const isGenerating = computed(() => store.isGenerating)
const progressPercent = ref(0)
const progressMessage = ref('')

const handleGenerate = async () => {
  if (!store.text.trim()) {
    ElMessage.error(t('error.input_required'))
    return
  }
  if (!store.frameTemplate) {
    ElMessage.warning(t('template.select'))
    return
  }

  store.isGenerating = true
  progressPercent.value = 0
  progressMessage.value = t('status.initializing')

  try {
    const req = store.buildRequest()
    const { data } = await generateVideoAsync(req)
    store.currentTaskId = data.task_id

    ElMessage.success(t('status.generating'))

    // Poll task progress
    const pollInterval = setInterval(async () => {
      try {
        const { getTaskStatus } = await import('@/api/tasks')
        const { data: task } = await getTaskStatus(data.task_id)

        if (task.progress) {
          progressPercent.value = task.progress.percentage
          progressMessage.value = task.progress.message || ''
        }

        if (task.status === 'completed') {
          clearInterval(pollInterval)
          store.isGenerating = false
          ElMessage.success(t('status.success'))
          if (task.result?.video_url) {
            progressMessage.value = t('status.video_generated', { path: task.result.video_url })
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
</script>

<template>
  <div class="home-view animate-fade-in">
    <!-- Hero Section -->
    <div class="hero-section">
      <h1 class="hero-title">
        {{ t('progressive.pipeline.title') }}
      </h1>
      <p class="hero-subtitle">
        {{ t('progressive.pipeline.caption') }}
      </p>
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
            <el-icon :size="28">
              <component :is="pipelineIcons[p.key]" />
            </el-icon>
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
      <!-- Left: Input Section -->
      <div class="input-section">
        <!-- Content Input Card -->
        <div class="section-card">
          <div class="section-card-header">
            <el-icon class="section-icon"><Edit /></el-icon>
            <span>{{ t('section.content_input') }}</span>
          </div>
          <div class="section-card-body">
            <!-- Mode Selection -->
            <div class="mode-selector">
              <button
                class="mode-btn"
                :class="{ active: store.mode === 'generate' }"
                @click="store.mode = 'generate'"
              >
                <el-icon><Star /></el-icon>
                <span>{{ t('mode.generate') }}</span>
              </button>
              <button
                class="mode-btn"
                :class="{ active: store.mode === 'fixed' }"
                @click="store.mode = 'fixed'"
              >
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
                :rows="5"
                :placeholder="
                  store.mode === 'generate'
                    ? t('input.topic_placeholder')
                    : t('input.content_placeholder')
                "
                class="content-textarea"
              />
            </div>

            <!-- Title & Scenes -->
            <div class="input-row">
              <div class="input-group flex-1">
                <label class="input-label">{{ t('input.title') }}</label>
                <el-input
                  v-model="store.title"
                  :placeholder="t('input.title_placeholder')"
                />
              </div>
              <div class="input-group scenes-group">
                <label class="input-label">{{ t('video.frames') }}</label>
                <div class="scenes-control">
                  <el-slider
                    v-model="store.nScenes"
                    :min="1"
                    :max="20"
                    :show-tooltip="false"
                  />
                  <span class="scenes-value">{{ store.nScenes }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Settings Section -->
      <div class="settings-section">
        <!-- Template Card -->
        <div class="section-card">
          <div class="section-card-header">
            <el-icon class="section-icon"><Picture /></el-icon>
            <span>{{ t('template.selector') }}</span>
          </div>
          <div class="section-card-body">
            <el-select
              v-model="store.frameTemplate"
              :placeholder="t('template.select')"
              class="full-select"
              filterable
            >
              <el-option
                v-for="tmpl in templates"
                :key="tmpl.key"
                :label="`${tmpl.name} (${tmpl.width}x${tmpl.height})`"
                :value="tmpl.key"
              />
            </el-select>
          </div>
        </div>

        <!-- Workflow Card -->
        <div class="section-card">
          <div class="section-card-header">
            <el-icon class="section-icon"><Brush /></el-icon>
            <span>{{ t('style.workflow') }}</span>
          </div>
          <div class="section-card-body">
            <div class="workflow-group">
              <label class="input-label">
                <el-icon><Mic /></el-icon>
                {{ t('tts.selector') }}
              </label>
              <el-select
                v-model="store.ttsWorkflow"
                :placeholder="t('tts.selector')"
                class="full-select"
                clearable
              >
                <el-option
                  v-for="wf in ttsWorkflows"
                  :key="wf.key"
                  :label="wf.display_name"
                  :value="wf.key"
                />
              </el-select>
            </div>

            <div class="workflow-group">
              <label class="input-label">
                <el-icon><VideoCamera /></el-icon>
                {{ t('style.workflow') }}
              </label>
              <el-select
                v-model="store.mediaWorkflow"
                :placeholder="t('style.workflow')"
                class="full-select"
                clearable
              >
                <el-option
                  v-for="wf in mediaWorkflows"
                  :key="wf.key"
                  :label="wf.display_name"
                  :value="wf.key"
                />
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
            <div class="bgm-group">
              <el-select
                v-model="store.bgmPath"
                :placeholder="t('bgm.selector')"
                class="full-select"
                clearable
              >
                <el-option :label="t('bgm.none')" :value="''" />
                <el-option
                  v-for="bgm in bgmFiles"
                  :key="bgm.path"
                  :label="bgm.name"
                  :value="bgm.path"
                />
              </el-select>
            </div>
            <div class="volume-control">
              <label class="input-label">{{ t('bgm.volume') }}</label>
              <el-slider
                v-model="store.bgmVolume"
                :min="0"
                :max="1"
                :step="0.05"
                :format-tooltip="(val: number) => `${Math.round(val * 100)}%`"
              />
            </div>
          </div>
        </div>

        <!-- Prompt Prefix -->
        <div class="section-card">
          <div class="section-card-header">
            <el-icon class="section-icon"><Document /></el-icon>
            <span>{{ t('style.prompt_prefix') }}</span>
          </div>
          <div class="section-card-body">
            <el-input
              v-model="store.promptPrefix"
              :placeholder="t('style.prompt_prefix_placeholder')"
            />
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
              <el-progress
                :percentage="progressPercent"
                :stroke-width="10"
                :show-text="false"
                class="generate-progress"
              />
              <span class="progress-text">{{ Math.round(progressPercent) }}%</span>
            </div>
          </transition>
        </div>
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
  .pipeline-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .pipeline-grid {
    grid-template-columns: repeat(2, 1fr);
  }
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

.pipeline-card:hover .pipeline-card-icon {
  transform: scale(1.1);
}

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
  .content-area {
    grid-template-columns: 1fr;
  }
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

/* Mode Selector */
.mode-selector {
  display: flex;
  gap: var(--pv-space-2);
  padding: var(--pv-space-1);
  background: var(--pv-bg);
  border-radius: var(--pv-radius);
  margin-bottom: var(--pv-space-5);
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

.flex-1 {
  flex: 1;
}

.scenes-group {
  width: 200px;
}

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

/* Selects */
.full-select {
  width: 100%;
}

/* Workflow Groups */
.workflow-group {
  margin-bottom: var(--pv-space-4);
}

.workflow-group:last-child {
  margin-bottom: 0;
}

.workflow-group .input-label .el-icon {
  font-size: 14px;
}

/* BGM */
.bgm-group {
  margin-bottom: var(--pv-space-4);
}

.volume-control .el-slider {
  margin-top: var(--pv-space-2);
}

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

.generate-btn:active {
  transform: translateY(0);
}

.generate-btn .el-icon {
  margin-right: var(--pv-space-2);
}

.progress-container {
  display: flex;
  align-items: center;
  gap: var(--pv-space-3);
  margin-top: var(--pv-space-4);
}

.generate-progress {
  flex: 1;
}

.generate-progress :deep(.el-progress-bar__inner) {
  background: linear-gradient(90deg, var(--pv-primary-light), #7c3aed);
}

.progress-text {
  font-weight: 600;
  font-size: 14px;
  color: var(--pv-primary);
  min-width: 40px;
}

/* Transitions */
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}

.slide-fade-enter-from {
  transform: translateY(-10px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}
</style>
