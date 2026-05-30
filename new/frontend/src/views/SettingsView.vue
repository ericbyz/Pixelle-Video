<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import {
  Setting,
  Link,
  Refresh,
  Connection,
  Check,
  Cpu,
  Picture,
  VideoCamera,
  Monitor,
} from '@element-plus/icons-vue'
import { useConfigStore } from '@/stores/config'

const { t, locale } = useI18n()
const configStore = useConfigStore()

const activeTab = ref('llm')

// LLM preset selection
const handlePresetChange = (presetName: string) => {
  configStore.applyPreset(presetName)
  configStore.loadedModels = []
}

// Load models from API
const handleLoadModels = async () => {
  try {
    const models = await configStore.fetchModels()
    ElMessage.success(t('settings.llm.models_loaded').replace('{count}', String(models.length)))
  } catch (e: any) {
    ElMessage.error(t('settings.llm.models_load_failed').replace('{error}', e.message || ''))
  }
}

// Test connection
const handleTestConnection = async () => {
  try {
    const res = await configStore.testConnection()
    if (res.success) {
      ElMessage.success(res.message || t('status.connection_success'))
    } else {
      ElMessage.error(res.message || t('status.connection_failed'))
    }
  } catch (e: any) {
    ElMessage.error(t('settings.llm.connection_failed').replace('{error}', e.message || ''))
  }
}

// Save config
const handleSaveConfig = async () => {
  try {
    await configStore.save()
    ElMessage.success(t('status.config_saved'))
  } catch (e: any) {
    ElMessage.error(t('status.save_failed'))
  }
}

// Reset config
const handleResetConfig = () => {
  configStore.reset()
  ElMessage.success(t('status.config_reset'))
}

// Model selection change
const handleModelChange = (val: string) => {
  if (val !== configStore.CUSTOM_MODEL_SENTINEL) {
    configStore.llm.model = val
  }
}

// Image preset change
const handleImagePresetChange = (presetName: string) => {
  configStore.applyImagePreset(presetName)
}

// Video preset change
const handleVideoPresetChange = (presetName: string) => {
  configStore.applyVideoPreset(presetName)
}

// RunningHub instance type
const is48G = computed({
  get: () => configStore.comfyui.runninghub_instance_type === 'plus',
  set: (val: boolean) => {
    configStore.comfyui.runninghub_instance_type = val ? 'plus' : ''
  },
})

onMounted(async () => {
  await Promise.all([
    configStore.loadPresets(),
    configStore.loadConfig(),
    configStore.loadImagePresets(),
    configStore.loadVideoPresets(),
  ])
})
</script>

<template>
  <div class="settings-view animate-fade-in">
    <!-- Hero -->
    <div class="settings-hero">
      <h1 class="settings-title">{{ t('settings.title') || '系统设置' }}</h1>
      <p class="settings-subtitle">{{ t('settings.subtitle') || '配置大语言模型、图片和视频生成服务' }}</p>
    </div>

    <!-- Tabs -->
    <el-tabs v-model="activeTab" class="settings-tabs">
      <!-- ==================== LLM Tab ==================== -->
      <el-tab-pane name="llm">
        <template #label>
          <div class="tab-label">
            <el-icon><Cpu /></el-icon>
            <span>{{ t('settings.llm.title') || '大语言模型' }}</span>
          </div>
        </template>

        <div class="tab-content">
          <!-- Preset Selection -->
          <div class="settings-section">
            <h3 class="section-title">{{ t('settings.llm.quick_select') || '快速选择' }}</h3>
            <div class="preset-grid">
              <div
                v-for="preset in configStore.llmPresets"
                :key="preset.name"
                class="preset-card"
                :class="{ active: configStore.llm.base_url === preset.base_url }"
                @click="handlePresetChange(preset.name)"
              >
                <div class="preset-card-name">{{ preset.name }}</div>
                <div class="preset-card-model">{{ preset.model }}</div>
                <div class="preset-card-check" v-if="configStore.llm.base_url === preset.base_url">
                  <el-icon><Check /></el-icon>
                </div>
              </div>
              <div
                class="preset-card"
                :class="{ active: configStore.selectedPreset === 'Custom' }"
                @click="handlePresetChange('Custom')"
              >
                <div class="preset-card-name">Custom</div>
                <div class="preset-card-model">{{ t('settings.llm.custom_model') || '自定义配置' }}</div>
                <div class="preset-card-check" v-if="configStore.selectedPreset === 'Custom'">
                  <el-icon><Check /></el-icon>
                </div>
              </div>
            </div>
          </div>

          <!-- Config Form -->
          <div class="settings-section">
            <h3 class="section-title">{{ t('settings.llm.config') || '详细配置' }}</h3>
            <div class="config-form">
              <!-- API Key URL Link -->
              <div v-if="configStore.currentApiKeyUrl" class="api-key-link">
                <el-link :href="configStore.currentApiKeyUrl" target="_blank" type="primary">
                  <el-icon><Link /></el-icon>
                  {{ t('settings.llm.get_api_key') || '获取 API Key' }}
                </el-link>
              </div>

              <!-- API Key -->
              <div class="form-group">
                <label class="form-label">
                  {{ t('settings.llm.api_key') || 'API Key' }}
                  <span class="required">*</span>
                </label>
                <el-input
                  v-model="configStore.llm.api_key"
                  :placeholder="t('settings.llm.api_key_help') || '请输入 API Key'"
                  type="password"
                  show-password
                />
              </div>

              <!-- Base URL -->
              <div class="form-group">
                <label class="form-label">
                  {{ t('settings.llm.base_url') || '服务地址' }}
                  <span class="required">*</span>
                </label>
                <el-input
                  v-model="configStore.llm.base_url"
                  :placeholder="t('settings.llm.base_url_help') || '请输入 API Base URL'"
                />
              </div>

              <!-- Model Selection -->
              <div class="form-group">
                <label class="form-label">
                  {{ t('settings.llm.model') || '模型' }}
                  <span class="required">*</span>
                </label>
                <!-- Show preset models if available -->
                <el-select
                  v-if="configStore.currentPresetModels.length > 0"
                  v-model="configStore.llm.model"
                  filterable
                  class="w-full"
                  :placeholder="t('settings.llm.model') || '选择模型'"
                >
                  <el-option
                    v-for="m in configStore.currentPresetModels"
                    :key="m.id"
                    :label="m.name"
                    :value="m.id"
                  />
                </el-select>
                <!-- Show loaded models or custom input -->
                <template v-else>
                  <el-select
                    v-model="configStore.currentModelSelection"
                    filterable
                    class="w-full"
                    @change="handleModelChange"
                  >
                    <el-option
                      :label="t('settings.llm.custom_model') || '自定义模型'"
                      :value="configStore.CUSTOM_MODEL_SENTINEL"
                    />
                    <el-option
                      v-for="m in configStore.loadedModels"
                      :key="m"
                      :label="m"
                      :value="m"
                    />
                  </el-select>
                  <el-input
                    v-if="configStore.currentModelSelection === configStore.CUSTOM_MODEL_SENTINEL"
                    v-model="configStore.llm.model"
                    :placeholder="t('settings.llm.custom_model_input') || '输入模型名称'"
                    class="mt-3"
                  />
                </template>
              </div>

              <!-- Actions -->
              <div class="form-actions">
                <el-button
                  :loading="configStore.isLoadingModels"
                  @click="handleLoadModels"
                  :icon="Refresh"
                >
                  {{ t('settings.llm.load_models') || '加载模型' }}
                </el-button>
                <el-button
                  :loading="configStore.isTesting"
                  @click="handleTestConnection"
                  :icon="Connection"
                >
                  {{ t('settings.llm.test_connection') || '测试连接' }}
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- ==================== Image Service Tab ==================== -->
      <el-tab-pane name="image">
        <template #label>
          <div class="tab-label">
            <el-icon><Picture /></el-icon>
            <span>{{ t('settings.image_service.title') || '图片生成服务' }}</span>
          </div>
        </template>

        <div class="tab-content">
          <!-- Provider Selection -->
          <div class="settings-section">
            <h3 class="section-title">{{ t('settings.image_service.select_provider') || '选择服务商' }}</h3>
            <div class="provider-grid">
              <div
                class="provider-card"
                :class="{ active: configStore.imageService.provider === 'comfyui' }"
                @click="configStore.imageService.provider = 'comfyui'; configStore.selectedImagePreset = ''"
              >
                <div class="provider-icon comfyui">C</div>
                <div class="provider-name">ComfyUI</div>
                <div class="provider-desc">{{ t('settings.image_service.comfyui_desc') || '本地或云端 ComfyUI 工作流' }}</div>
              </div>
              <div
                v-for="preset in configStore.imagePresets"
                :key="preset.name"
                class="provider-card"
                :class="{ active: configStore.imageService.base_url === preset.base_url }"
                @click="handleImagePresetChange(preset.name)"
              >
                <div class="provider-icon" :class="preset.provider">
                  {{ preset.provider.charAt(0).toUpperCase() }}
                </div>
                <div class="provider-name">{{ preset.name }}</div>
                <div class="provider-desc">{{ preset.description }}</div>
                <div class="provider-check" v-if="configStore.imageService.base_url === preset.base_url">
                  <el-icon><Check /></el-icon>
                </div>
              </div>
            </div>
          </div>

          <!-- Config Form (non-ComfyUI) -->
          <div class="settings-section" v-if="configStore.imageService.provider !== 'comfyui'">
            <h3 class="section-title">{{ t('settings.image_service.config') || '服务配置' }}</h3>
            <div class="config-form">
              <div v-if="configStore.currentImageApiKeyUrl" class="api-key-link">
                <el-link :href="configStore.currentImageApiKeyUrl" target="_blank" type="primary">
                  <el-icon><Link /></el-icon>
                  {{ t('settings.llm.get_api_key') || '获取 API Key' }}
                </el-link>
              </div>

              <div class="form-group">
                <label class="form-label">
                  API Key
                  <span class="required">*</span>
                </label>
                <el-input
                  v-model="configStore.imageService.api_key"
                  placeholder="请输入图片服务 API Key"
                  type="password"
                  show-password
                />
              </div>

              <div class="form-group">
                <label class="form-label">
                  {{ t('settings.llm.base_url') || '服务地址' }}
                  <span class="required">*</span>
                </label>
                <el-input v-model="configStore.imageService.base_url" placeholder="API Base URL" />
              </div>

              <div class="form-group">
                <label class="form-label">{{ t('settings.llm.model') || '模型' }}</label>
                <el-select
                  v-if="configStore.currentImageModels.length > 0"
                  v-model="configStore.imageService.model"
                  filterable
                  class="w-full"
                >
                  <el-option
                    v-for="m in configStore.currentImageModels"
                    :key="m.id"
                    :label="m.name"
                    :value="m.id"
                  />
                </el-select>
                <el-input v-else v-model="configStore.imageService.model" placeholder="输入模型 ID" />
              </div>
            </div>
          </div>

          <!-- ComfyUI hint -->
          <div class="settings-section" v-else>
            <div class="comfyui-hint">
              <el-icon :size="20"><Monitor /></el-icon>
              <span>使用 ComfyUI 进行图片生成，请在下方 ComfyUI 配置标签页中设置 ComfyUI 服务地址和工作流。</span>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- ==================== Video Service Tab ==================== -->
      <el-tab-pane name="video">
        <template #label>
          <div class="tab-label">
            <el-icon><VideoCamera /></el-icon>
            <span>{{ t('settings.video_service.title') || '视频生成服务' }}</span>
          </div>
        </template>

        <div class="tab-content">
          <!-- Provider Selection -->
          <div class="settings-section">
            <h3 class="section-title">{{ t('settings.video_service.select_provider') || '选择服务商' }}</h3>
            <div class="provider-grid">
              <div
                class="provider-card"
                :class="{ active: configStore.videoService.provider === 'comfyui' }"
                @click="configStore.videoService.provider = 'comfyui'; configStore.selectedVideoPreset = ''"
              >
                <div class="provider-icon comfyui">C</div>
                <div class="provider-name">ComfyUI</div>
                <div class="provider-desc">{{ t('settings.video_service.comfyui_desc') || '本地或云端 ComfyUI 工作流' }}</div>
              </div>
              <div
                v-for="preset in configStore.videoPresets"
                :key="preset.name"
                class="provider-card"
                :class="{ active: configStore.videoService.base_url === preset.base_url }"
                @click="handleVideoPresetChange(preset.name)"
              >
                <div class="provider-icon" :class="preset.provider">
                  {{ preset.provider.charAt(0).toUpperCase() }}
                </div>
                <div class="provider-name">{{ preset.name }}</div>
                <div class="provider-desc">{{ preset.description }}</div>
                <div class="provider-check" v-if="configStore.videoService.base_url === preset.base_url">
                  <el-icon><Check /></el-icon>
                </div>
              </div>
            </div>
          </div>

          <!-- Config Form (non-ComfyUI) -->
          <div class="settings-section" v-if="configStore.videoService.provider !== 'comfyui'">
            <h3 class="section-title">{{ t('settings.video_service.config') || '服务配置' }}</h3>
            <div class="config-form">
              <div v-if="configStore.currentVideoApiKeyUrl" class="api-key-link">
                <el-link :href="configStore.currentVideoApiKeyUrl" target="_blank" type="primary">
                  <el-icon><Link /></el-icon>
                  {{ t('settings.llm.get_api_key') || '获取 API Key' }}
                </el-link>
              </div>

              <div class="form-group">
                <label class="form-label">
                  API Key
                  <span class="required">*</span>
                </label>
                <el-input
                  v-model="configStore.videoService.api_key"
                  placeholder="请输入视频服务 API Key"
                  type="password"
                  show-password
                />
              </div>

              <div class="form-group">
                <label class="form-label">
                  {{ t('settings.llm.base_url') || '服务地址' }}
                  <span class="required">*</span>
                </label>
                <el-input v-model="configStore.videoService.base_url" placeholder="API Base URL" />
              </div>

              <div class="form-group">
                <label class="form-label">{{ t('settings.llm.model') || '模型' }}</label>
                <el-select
                  v-if="configStore.currentVideoModels.length > 0"
                  v-model="configStore.videoService.model"
                  filterable
                  class="w-full"
                >
                  <el-option
                    v-for="m in configStore.currentVideoModels"
                    :key="m.id"
                    :label="m.name"
                    :value="m.id"
                  />
                </el-select>
                <el-input v-else v-model="configStore.videoService.model" placeholder="输入模型 ID" />
              </div>
            </div>
          </div>

          <!-- ComfyUI hint -->
          <div class="settings-section" v-else>
            <div class="comfyui-hint">
              <el-icon :size="20"><Monitor /></el-icon>
              <span>使用 ComfyUI 进行视频生成，请在下方 ComfyUI 配置标签页中设置 ComfyUI 服务地址和工作流。</span>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- ==================== ComfyUI Tab ==================== -->
      <el-tab-pane name="comfyui">
        <template #label>
          <div class="tab-label">
            <el-icon><Monitor /></el-icon>
            <span>ComfyUI</span>
          </div>
        </template>

        <div class="tab-content">
          <!-- Local ComfyUI -->
          <div class="settings-section">
            <h3 class="section-title">{{ t('settings.comfyui.local_title') || '本地 ComfyUI' }}</h3>
            <div class="config-form">
              <div class="form-group">
                <label class="form-label">{{ t('settings.comfyui.comfyui_url') || 'ComfyUI 地址' }}</label>
                <el-input
                  v-model="configStore.comfyui.comfyui_url"
                  :placeholder="t('settings.comfyui.comfyui_url_help') || 'http://127.0.0.1:8188'"
                />
              </div>
              <div class="form-group">
                <label class="form-label">{{ t('settings.comfyui.comfyui_api_key') || 'API Key' }}</label>
                <el-input
                  v-model="configStore.comfyui.comfyui_api_key"
                  :placeholder="t('settings.comfyui.comfyui_api_key_help') || '可选'"
                  type="password"
                  show-password
                />
              </div>
            </div>
          </div>

          <!-- RunningHub Cloud -->
          <div class="settings-section">
            <h3 class="section-title">{{ t('settings.comfyui.cloud_title') || 'RunningHub 云端' }}</h3>
            <div class="config-form">
              <div class="form-group">
                <label class="form-label">{{ t('settings.comfyui.runninghub_api_key') || 'RunningHub API Key' }}</label>
                <el-input
                  v-model="configStore.comfyui.runninghub_api_key"
                  :placeholder="t('settings.comfyui.runninghub_api_key_help') || '请输入 RunningHub API Key'"
                  type="password"
                  show-password
                />
              </div>
              <div class="runninghub-link">
                <el-link
                  :href="locale === 'zh-CN' ? 'https://www.runninghub.cn/?inviteCode=bozpdlbj' : 'https://www.runninghub.ai/?inviteCode=bozpdlbj'"
                  target="_blank"
                  type="primary"
                >
                  {{ t('settings.comfyui.runninghub_get_api_key') || '获取 RunningHub API Key' }}
                </el-link>
              </div>
              <div class="form-row">
                <div class="form-group flex-1">
                  <label class="form-label">{{ t('settings.comfyui.runninghub_concurrent_limit') || '并发数' }}</label>
                  <el-input-number
                    v-model="configStore.comfyui.runninghub_concurrent_limit"
                    :min="1"
                    :max="10"
                    class="w-full"
                  />
                </div>
                <div class="form-group flex-1">
                  <label class="form-label">{{ t('settings.comfyui.runninghub_instance_type') || '实例类型' }}</label>
                  <el-select v-model="is48G" class="w-full">
                    <el-option :label="t('settings.comfyui.runninghub_instance_24g') || '24GB'" :value="false" />
                    <el-option :label="t('settings.comfyui.runninghub_instance_48g') || '48GB'" :value="true" />
                  </el-select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Save / Reset Bar -->
    <div class="settings-footer">
      <el-button
        type="primary"
        size="large"
        class="save-btn"
        :loading="configStore.isSaving"
        @click="handleSaveConfig"
      >
        <el-icon><Check /></el-icon>
        {{ t('btn.save_config') || '保存配置' }}
      </el-button>
      <el-button
        size="large"
        class="reset-btn"
        @click="handleResetConfig"
      >
        {{ t('btn.reset_config') || '重置' }}
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.settings-view {
  max-width: 960px;
  margin: 0 auto;
  padding-bottom: var(--pv-space-10);
}

/* Hero */
.settings-hero {
  text-align: center;
  margin-bottom: var(--pv-space-8);
  padding: var(--pv-space-8) 0 var(--pv-space-4);
}

.settings-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--pv-text);
  margin-bottom: var(--pv-space-2);
  letter-spacing: -0.5px;
}

.settings-subtitle {
  font-size: 16px;
  color: var(--pv-text-secondary);
}

/* Tabs */
.settings-tabs :deep(.el-tabs__header) {
  margin-bottom: var(--pv-space-6);
}

.settings-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background: var(--pv-border-light);
}

.settings-tabs :deep(.el-tabs__active-bar) {
  height: 3px;
  border-radius: 2px;
  background: linear-gradient(90deg, var(--pv-primary), var(--pv-accent));
}

.settings-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 500;
  padding: 0 var(--pv-space-5);
  height: 48px;
  line-height: 48px;
}

.settings-tabs :deep(.el-tabs__item.is-active) {
  color: var(--pv-primary);
  font-weight: 600;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: var(--pv-space-2);
}

.tab-content {
  min-height: 400px;
}

/* Sections */
.settings-section {
  margin-bottom: var(--pv-space-8);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--pv-text);
  margin-bottom: var(--pv-space-4);
  padding-bottom: var(--pv-space-2);
  border-bottom: 1px solid var(--pv-border-light);
}

/* Preset Grid */
.preset-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: var(--pv-space-3);
}

.preset-card {
  position: relative;
  padding: var(--pv-space-4);
  background: var(--pv-surface);
  border: 2px solid var(--pv-border-light);
  border-radius: var(--pv-radius-lg);
  cursor: pointer;
  transition: all var(--pv-transition);
}

.preset-card:hover {
  border-color: var(--pv-primary-200);
  background: var(--pv-primary-50);
  transform: translateY(-1px);
  box-shadow: var(--pv-shadow-md);
}

.preset-card.active {
  border-color: var(--pv-primary);
  background: linear-gradient(135deg, var(--pv-primary-50), var(--pv-primary-100));
  box-shadow: 0 2px 12px rgb(99 102 241 / 0.15);
}

.preset-card-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--pv-text);
  margin-bottom: var(--pv-space-1);
}

.preset-card-model {
  font-size: 12px;
  color: var(--pv-text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.preset-card-check {
  position: absolute;
  top: var(--pv-space-2);
  right: var(--pv-space-2);
  color: var(--pv-primary);
  font-size: 18px;
}

/* Provider Grid */
.provider-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--pv-space-4);
}

.provider-card {
  position: relative;
  padding: var(--pv-space-5);
  background: var(--pv-surface);
  border: 2px solid var(--pv-border-light);
  border-radius: var(--pv-radius-xl);
  cursor: pointer;
  transition: all var(--pv-transition);
}

.provider-card:hover {
  border-color: var(--pv-primary-200);
  transform: translateY(-2px);
  box-shadow: var(--pv-shadow-lg);
}

.provider-card.active {
  border-color: var(--pv-primary);
  background: linear-gradient(135deg, var(--pv-primary-50), var(--pv-primary-100));
  box-shadow: 0 4px 20px rgb(99 102 241 / 0.2);
}

.provider-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--pv-radius-lg);
  font-size: 18px;
  font-weight: 700;
  margin-bottom: var(--pv-space-3);
  color: white;
}

.provider-icon.comfyui {
  background: linear-gradient(135deg, #10b981, #059669);
}

.provider-icon.volcengine {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.provider-icon.doubao {
  background: linear-gradient(135deg, #8b5cf6, #6d28d9);
}

.provider-icon.qwen {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.provider-icon.zhipu {
  background: linear-gradient(135deg, #06b6d4, #0891b2);
}

.provider-icon.kling {
  background: linear-gradient(135deg, #ec4899, #db2777);
}

.provider-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--pv-text);
  margin-bottom: var(--pv-space-1);
}

.provider-desc {
  font-size: 12px;
  color: var(--pv-text-muted);
  line-height: 1.4;
}

.provider-check {
  position: absolute;
  top: var(--pv-space-3);
  right: var(--pv-space-3);
  color: var(--pv-primary);
  font-size: 20px;
}

/* Config Form */
.config-form {
  background: var(--pv-surface);
  border: 1px solid var(--pv-border-light);
  border-radius: var(--pv-radius-lg);
  padding: var(--pv-space-6);
}

.form-group {
  margin-bottom: var(--pv-space-5);
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--pv-text-secondary);
  margin-bottom: var(--pv-space-2);
}

.required {
  color: var(--pv-danger);
  margin-left: 2px;
}

.form-row {
  display: flex;
  gap: var(--pv-space-4);
}

.flex-1 {
  flex: 1;
}

.form-actions {
  display: flex;
  gap: var(--pv-space-3);
  margin-top: var(--pv-space-5);
  padding-top: var(--pv-space-5);
  border-top: 1px solid var(--pv-border-light);
}

.api-key-link {
  margin-bottom: var(--pv-space-4);
}

.api-key-link .el-link {
  font-size: 13px;
}

.runninghub-link {
  margin-bottom: var(--pv-space-4);
}

.runninghub-link .el-link {
  font-size: 13px;
}

.comfyui-hint {
  display: flex;
  align-items: flex-start;
  gap: var(--pv-space-3);
  padding: var(--pv-space-5);
  background: var(--pv-surface);
  border: 1px solid var(--pv-border-light);
  border-radius: var(--pv-radius-lg);
  color: var(--pv-text-secondary);
  font-size: 14px;
  line-height: 1.6;
}

.comfyui-hint .el-icon {
  color: var(--pv-primary);
  margin-top: 2px;
  flex-shrink: 0;
}

.w-full {
  width: 100%;
}

.mt-3 {
  margin-top: var(--pv-space-3);
}

/* Footer */
.settings-footer {
  display: flex;
  gap: var(--pv-space-3);
  padding: var(--pv-space-6) 0;
  border-top: 1px solid var(--pv-border-light);
  margin-top: var(--pv-space-4);
}

.save-btn {
  flex: 1;
  height: 48px;
  font-size: 15px;
  font-weight: 600;
  border-radius: var(--pv-radius-lg);
  background: linear-gradient(135deg, var(--pv-primary), #7c3aed);
  border: none;
  box-shadow: 0 4px 16px rgb(99 102 241 / 0.3);
}

.save-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgb(99 102 241 / 0.4);
}

.save-btn .el-icon {
  margin-right: var(--pv-space-2);
}

.reset-btn {
  height: 48px;
  font-size: 15px;
  border-radius: var(--pv-radius-lg);
}
</style>
