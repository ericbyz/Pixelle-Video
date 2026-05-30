<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import {
  HomeFilled,
  Clock,
  Setting,
  VideoCamera,
  ChatRound,
  Search,
  FolderOpened,
  Collection,
  UserFilled,
  Plus,
  Star,
  Monitor,
  Film,
  Position,
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
  return '/home'
})

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
</script>

<template>
  <div class="app-shell">
    <aside class="icon-rail">
      <button class="brand-dot" @click="router.push('/home')" aria-label="Pixelle Video">
        <el-icon><VideoCamera /></el-icon>
      </button>

      <nav class="rail-nav">
        <button class="rail-btn active" @click="router.push('/home')" :title="t('nav.home')">
          <el-icon><ChatRound /></el-icon>
        </button>
        <button class="rail-btn" :title="t('nav.history')" @click="router.push('/history')">
          <el-icon><Clock /></el-icon>
        </button>
        <button class="rail-btn" :title="t('nav.settings')" @click="router.push('/settings')">
          <el-icon><Setting /></el-icon>
        </button>
        <button class="rail-btn" title="Search">
          <el-icon><Search /></el-icon>
        </button>
        <button class="rail-btn" title="Assets">
          <el-icon><Collection /></el-icon>
        </button>
      </nav>

      <div class="rail-footer">
        <el-select
          v-model="currentLanguage"
          size="small"
          class="rail-lang"
          placement="right"
        >
          <el-option
            v-for="lang in languageOptions"
            :key="lang.value"
            :label="lang.label"
            :value="lang.value"
          />
        </el-select>
        <button class="profile-dot" title="Profile">
          <el-icon><UserFilled /></el-icon>
        </button>
      </div>
    </aside>

    <aside class="flow-sidebar">
      <div class="sidebar-top">
        <button class="sidebar-title" @click="router.push('/home')">
          <span>视频创作</span>
          <span class="sidebar-caret">⌄</span>
        </button>
        <button class="new-btn" @click="router.push('/home')" title="New">
          <el-icon><Plus /></el-icon>
        </button>
      </div>

      <div class="flow-list">
        <button
          v-for="pipeline in pipelines"
          :key="pipeline.key"
          class="flow-item"
          :class="{ active: activeMenu === '/home' && pipelineStore.currentPipeline === pipeline.key }"
          @click="selectPipeline(pipeline.key)"
        >
          <span class="flow-avatar">
            <el-icon><component :is="pipelineIcons[pipeline.key]" /></el-icon>
          </span>
          <span class="flow-copy">
            <strong>{{ pipeline.name }}</strong>
            <span>{{ pipeline.desc }}</span>
          </span>
          <span class="flow-time">刚刚</span>
        </button>
      </div>

      <div class="sidebar-links">
        <button class="side-link" :class="{ active: activeMenu === '/history' }" @click="router.push('/history')">
          <el-icon><Clock /></el-icon>
          <span>{{ t('nav.history') }}</span>
        </button>
        <button class="side-link" :class="{ active: activeMenu === '/settings' }" @click="router.push('/settings')">
          <el-icon><Setting /></el-icon>
          <span>{{ t('nav.settings') || '设置' }}</span>
        </button>
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
  grid-template-columns: 64px 312px minmax(0, 1fr);
  height: 100vh;
  background: #f7f7f5;
  color: var(--pv-text);
}

.icon-rail {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  padding: 18px 0;
  background: #fbfbfa;
  border-right: 1px solid #eeeeeb;
}

.brand-dot,
.profile-dot,
.rail-btn,
.new-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 0;
  cursor: pointer;
  transition: all var(--pv-transition);
}

.brand-dot {
  width: 34px;
  height: 34px;
  color: #ffffff;
  background: linear-gradient(145deg, #2f6df6, #ff5aac);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgb(47 109 246 / 0.24);
}

.rail-nav {
  display: grid;
  gap: 14px;
  margin-top: 22px;
}

.rail-btn {
  width: 38px;
  height: 38px;
  color: #9b9895;
  background: transparent;
  border-radius: 14px;
}

.rail-btn:hover,
.rail-btn.active {
  color: #111111;
  background: #eeeeeb;
}

.rail-footer {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.rail-lang {
  width: 44px;
}

.rail-lang :deep(.el-input__wrapper) {
  min-height: 30px;
  padding: 0 4px;
  border-radius: 14px;
  background: #ffffff;
}

.rail-lang :deep(.el-input__inner) {
  font-size: 0;
}

.profile-dot {
  width: 36px;
  height: 36px;
  color: #ffffff;
  background: #3b82f6;
  border-radius: 50%;
}

.flow-sidebar {
  display: flex;
  flex-direction: column;
  min-width: 0;
  padding: 16px 12px;
  background: #ffffff;
  border-right: 1px solid #ececea;
}

.sidebar-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 4px 14px;
}

.sidebar-title {
  display: flex;
  align-items: center;
  gap: 6px;
  border: 0;
  background: transparent;
  color: #161514;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
}

.sidebar-caret {
  color: #7b7875;
  font-size: 18px;
}

.new-btn {
  width: 28px;
  height: 28px;
  color: #111111;
  background: transparent;
  border: 1px solid #dedbd7;
  border-radius: 50%;
}

.new-btn:hover {
  background: #f3f2ef;
}

.flow-list {
  display: grid;
  gap: 8px;
  overflow-y: auto;
  padding-right: 2px;
}

.flow-item {
  position: relative;
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr) auto;
  gap: 10px;
  width: 100%;
  min-height: 68px;
  padding: 8px 10px;
  text-align: left;
  background: transparent;
  border: 0;
  border-radius: 16px;
  cursor: pointer;
  transition: all var(--pv-transition);
}

.flow-item:hover,
.flow-item.active {
  background: #f4f4f2;
}

.flow-avatar {
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  color: #1f2937;
  background: #e9f1ec;
  border-radius: 50%;
  font-size: 18px;
}

.flow-item:nth-child(2) .flow-avatar { background: #e7efe6; }
.flow-item:nth-child(3) .flow-avatar { background: #edf0f6; }
.flow-item:nth-child(4) .flow-avatar { background: #f2ede5; }
.flow-item:nth-child(5) .flow-avatar { background: #e9edf7; }

.flow-copy {
  display: grid;
  align-content: center;
  min-width: 0;
}

.flow-copy strong {
  color: #1a1918;
  font-size: 14px;
  line-height: 1.25;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.flow-copy span {
  color: #8d8985;
  font-size: 12px;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.flow-time {
  color: #b0aca7;
  font-size: 12px;
  padding-top: 6px;
}

.sidebar-links {
  display: grid;
  gap: 6px;
  margin-top: auto;
  padding-top: 18px;
}

.side-link {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 38px;
  padding: 0 10px;
  color: #6f6a66;
  background: transparent;
  border: 0;
  border-radius: 12px;
  font-size: 13px;
  cursor: pointer;
}

.side-link:hover,
.side-link.active {
  color: #161514;
  background: #f4f4f2;
}

.app-main {
  min-width: 0;
  padding: 12px;
  background: #f7f7f5;
  overflow: hidden;
}

.main-surface {
  height: 100%;
  overflow: hidden;
  background: #ffffff;
  border: 1px solid #ececea;
  border-radius: 28px;
  box-shadow: 0 18px 50px rgb(20 20 20 / 0.05);
}

@media (max-width: 980px) {
  .app-shell {
    grid-template-columns: 56px minmax(0, 1fr);
  }

  .flow-sidebar {
    display: none;
  }
}

@media (max-width: 720px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .icon-rail {
    display: none;
  }

  .app-main {
    padding: 0;
  }

  .main-surface {
    border-radius: 0;
  }
}

/* Page Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
