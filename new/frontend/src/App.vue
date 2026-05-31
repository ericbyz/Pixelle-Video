<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import {
  Clock,
  Setting,
  VideoCamera,
  FolderOpened,
  Star,
  Monitor,
  Film,
  Position,
  TrendCharts,
  DataAnalysis,
} from '@element-plus/icons-vue'
import { usePipelineStore } from '@/stores/pipeline'
import type { PipelineType } from '@/types'

const { t, locale } = useI18n()
const router = useRouter()
const pipelineStore = usePipelineStore()

const activeMenu = computed(() => {
  const path = router.currentRoute.value.path
  if (path === '/history') return '/history'
  if (path === '/settings') return '/settings'
  if (path === '/usage') return '/usage'
  return '/home'
})

// Auto-switch tab based on route
const activeTab = ref('create')
watch(activeMenu, (val) => {
  if (val === '/home') activeTab.value = 'create'
  else if (val === '/history' || val === '/usage') activeTab.value = 'manage'
  else if (val === '/settings') activeTab.value = 'settings'
}, { immediate: true })

const tabs = computed(() => [
  { key: 'create', label: t('sidebar.create') },
  { key: 'manage', label: t('sidebar.manage') },
  { key: 'settings', label: t('sidebar.settings') },
])

const currentLanguage = computed({
  get: () => locale.value,
  set: (val: string) => {
    locale.value = val
    localStorage.setItem('locale', val)
  },
})

const languageOptions = [
  { label: '简体中文', value: 'zh-CN' },
  { label: 'English', value: 'en-US' },
]

const pipelineIcons: Record<PipelineType, any> = {
  quick_create: Star,
  custom_media: FolderOpened,
  digital_human: Monitor,
  image_to_video: Film,
  action_transfer: Position,
}

const pipelines = computed(() => [
  { key: 'quick_create' as PipelineType, name: t('pipeline.quick_create.name'), desc: t('pipeline.quick_create.description') },
  { key: 'custom_media' as PipelineType, name: t('pipeline.custom_media.name'), desc: t('pipeline.custom_media.description') },
  { key: 'digital_human' as PipelineType, name: t('pipeline.digital_human.name'), desc: t('pipeline.digital_human.description') },
  { key: 'image_to_video' as PipelineType, name: t('pipeline.i2v.name'), desc: t('pipeline.i2v.description') },
  { key: 'action_transfer' as PipelineType, name: t('pipeline.action_transfer.name'), desc: t('pipeline.action_transfer.description') },
])

const selectPipeline = (key: PipelineType) => {
  pipelineStore.currentPipeline = key
  router.push('/home')
}

function onTabClick(key: string) {
  activeTab.value = key
  if (key === 'create') router.push('/home')
  else if (key === 'manage') {
    if (activeMenu.value !== '/history' && activeMenu.value !== '/usage') router.push('/history')
  }
  else if (key === 'settings') router.push('/settings')
}
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <!-- Brand -->
      <div class="sidebar-brand" @click="router.push('/home')">
        <span class="brand-icon"><el-icon :size="18"><VideoCamera /></el-icon></span>
        <span class="brand-text">Pixelle Video</span>
      </div>

      <!-- Tabs -->
      <div class="sidebar-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="onTabClick(tab.key)"
        >{{ tab.label }}</button>
      </div>

      <!-- Tab: 创作 -->
      <div v-show="activeTab === 'create'" class="tab-panel">
        <div class="panel-hint">{{ t('sidebar.create_hint') }}</div>
        <button
          v-for="pipeline in pipelines"
          :key="pipeline.key"
          class="nav-item"
          :class="{ active: activeMenu === '/home' && pipelineStore.currentPipeline === pipeline.key }"
          @click="selectPipeline(pipeline.key)"
        >
          <span class="nav-icon"><el-icon><component :is="pipelineIcons[pipeline.key]" /></el-icon></span>
          <span class="nav-body">
            <span class="nav-text">{{ pipeline.name }}</span>
            <span class="nav-desc">{{ pipeline.desc }}</span>
          </span>
        </button>
      </div>

      <!-- Tab: 管理 -->
      <div v-show="activeTab === 'manage'" class="tab-panel">
        <button class="nav-item" :class="{ active: activeMenu === '/history' }" @click="router.push('/history')">
          <span class="nav-icon"><el-icon><Clock /></el-icon></span>
          <span class="nav-body">
            <span class="nav-text">{{ t('nav.history') }}</span>
            <span class="nav-desc">{{ t('sidebar.history_desc') }}</span>
          </span>
        </button>
        <button class="nav-item" :class="{ active: activeMenu === '/usage' }" @click="router.push('/usage')">
          <span class="nav-icon"><el-icon><TrendCharts /></el-icon></span>
          <span class="nav-body">
            <span class="nav-text">{{ t('nav.usage') }}</span>
            <span class="nav-desc">{{ t('sidebar.usage_desc') }}</span>
          </span>
        </button>
      </div>

      <!-- Tab: 设置 -->
      <div v-show="activeTab === 'settings'" class="tab-panel">
        <button class="nav-item" :class="{ active: activeMenu === '/settings' }" @click="router.push('/settings')">
          <span class="nav-icon"><el-icon><Setting /></el-icon></span>
          <span class="nav-body">
            <span class="nav-text">{{ t('nav.settings') }}</span>
            <span class="nav-desc">{{ t('sidebar.settings_desc') }}</span>
          </span>
        </button>
      </div>

      <!-- Footer -->
      <div class="sidebar-footer">
        <el-select v-model="currentLanguage" size="small" class="lang-select">
          <el-option
            v-for="lang in languageOptions"
            :key="lang.value"
            :label="lang.label"
            :value="lang.value"
          />
        </el-select>
      </div>
    </aside>

    <main class="app-main">
      <section class="main-surface">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </section>
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  height: 100vh;
  background: #f7f7f5;
  color: var(--pv-text);
}

/* ---- Sidebar ---- */
.sidebar {
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border-right: 1px solid #ececea;
  overflow: hidden;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px 18px 14px;
  cursor: pointer;
  user-select: none;
}

.brand-icon {
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  color: #ffffff;
  background: linear-gradient(145deg, #2f6df6, #ff5aac);
  border-radius: 9px;
  box-shadow: 0 4px 14px rgb(47 109 246 / 0.2);
  flex-shrink: 0;
}

.brand-text {
  font-size: 15px;
  font-weight: 700;
  color: #111827;
  letter-spacing: -0.01em;
}

/* ---- Tabs ---- */
.sidebar-tabs {
  display: flex;
  gap: 2px;
  padding: 0 14px;
  margin-bottom: 4px;
}

.tab-btn {
  flex: 1;
  padding: 7px 0;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: #9ca3af;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.tab-btn:hover {
  color: #6b7280;
  background: #f4f4f2;
}

.tab-btn.active {
  color: #4f46e5;
  background: #eef2ff;
}

/* ---- Tab Panel ---- */
.tab-panel {
  flex: 1;
  overflow-y: auto;
  padding: 6px 10px;
}

.panel-hint {
  font-size: 11px;
  color: #b0aca7;
  padding: 2px 8px 10px;
}

/* ---- Nav Items ---- */
.nav-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  width: 100%;
  padding: 10px 10px;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
}

.nav-item:hover {
  background: #f4f4f2;
  color: #111827;
}

.nav-item.active {
  background: #eef2ff;
  color: #4f46e5;
}

.nav-icon {
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  border-radius: 8px;
  font-size: 16px;
  flex-shrink: 0;
  background: #f3f4f6;
}

.nav-item.active .nav-icon {
  background: #e0e7ff;
}

.nav-body {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
  padding-top: 2px;
}

.nav-text {
  font-size: 13.5px;
  font-weight: 600;
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-desc {
  font-size: 11.5px;
  color: #9ca3af;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.nav-item.active .nav-desc {
  color: #818cf8;
}

/* ---- Footer ---- */
.sidebar-footer {
  padding: 10px 14px 16px;
  border-top: 1px solid #f3f3f0;
}

.lang-select {
  width: 100%;
}

.lang-select :deep(.el-input__wrapper) {
  border-radius: 8px;
}

/* ---- Main ---- */
.app-main {
  min-width: 0;
  padding: 12px;
  background: #f7f7f5;
  overflow: hidden;
}

.main-surface {
  height: 100%;
  overflow-y: auto;
  background: #ffffff;
  border: 1px solid #ececea;
  border-radius: 28px;
  box-shadow: 0 18px 50px rgb(20 20 20 / 0.05);
}

/* ---- Responsive ---- */
@media (max-width: 720px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    display: none;
  }

  .app-main {
    padding: 0;
  }

  .main-surface {
    border-radius: 0;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
