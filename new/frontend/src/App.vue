<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import {
  HomeFilled,
  Clock,
  Setting,
  ArrowLeft,
  ArrowRight,
  VideoCamera,
  Fold,
  Expand,
} from '@element-plus/icons-vue'

const { t, locale } = useI18n()
const router = useRouter()

const sidebarCollapsed = ref(false)
const activeMenu = computed(() => {
  const path = router.currentRoute.value.path
  if (path === '/history') return '/history'
  return '/home'
})

const currentLanguage = computed({
  get: () => locale.value,
  set: (val: string) => {
    locale.value = val
    localStorage.setItem('locale', val)
  },
})

const handleMenuSelect = (index: string) => {
  router.push(index)
}

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const languageOptions = [
  { label: '简体中文', value: 'zh-CN' },
  { label: 'English', value: 'en-US' },
]
</script>

<template>
  <el-container class="app-container">
    <!-- Top Navigation Bar -->
    <el-header class="app-header glass">
      <div class="header-left">
        <div class="app-logo">
          <el-icon :size="24" class="logo-icon"><VideoCamera /></el-icon>
          <span class="logo-text">Pixelle</span>
          <span class="logo-suffix">Video</span>
        </div>
      </div>

      <div class="header-center">
        <nav class="nav-menu">
          <router-link
            to="/home"
            class="nav-item"
            :class="{ active: activeMenu === '/home' }"
          >
            <el-icon><HomeFilled /></el-icon>
            <span>{{ t('nav.home') }}</span>
          </router-link>
          <router-link
            to="/history"
            class="nav-item"
            :class="{ active: activeMenu === '/history' }"
          >
            <el-icon><Clock /></el-icon>
            <span>{{ t('nav.history') }}</span>
          </router-link>
        </nav>
      </div>

      <div class="header-right">
        <el-select
          v-model="currentLanguage"
          size="small"
          class="lang-select"
        >
          <el-option
            v-for="lang in languageOptions"
            :key="lang.value"
            :label="lang.label"
            :value="lang.value"
          />
        </el-select>
      </div>
    </el-header>

    <el-container class="main-container">
      <!-- Sidebar -->
      <el-aside
        :width="sidebarCollapsed ? '64px' : '280px'"
        class="app-sidebar"
      >
        <div class="sidebar-header">
          <el-button
            :icon="sidebarCollapsed ? Expand : Fold"
            text
            class="sidebar-toggle"
            @click="toggleSidebar"
          />
        </div>

        <div class="sidebar-content" v-show="!sidebarCollapsed">
          <div class="sidebar-section">
            <h3 class="sidebar-section-title">
              <el-icon><Setting /></el-icon>
              <span>{{ t('settings.title') }}</span>
            </h3>

            <div class="config-card">
              <div class="config-group">
                <label class="config-label">{{ t('settings.llm.api_key') }}</label>
                <el-input
                  :placeholder="t('settings.llm.api_key_help')"
                  type="password"
                  show-password
                  size="small"
                />
              </div>

              <div class="config-group">
                <label class="config-label">{{ t('settings.llm.base_url') }}</label>
                <el-input
                  :placeholder="t('settings.llm.base_url_help')"
                  size="small"
                />
              </div>

              <div class="config-group">
                <label class="config-label">{{ t('settings.llm.model') }}</label>
                <el-input
                  :placeholder="t('settings.llm.model_help')"
                  size="small"
                />
              </div>

              <el-button type="primary" size="small" class="save-btn">
                {{ t('btn.save_config') }}
              </el-button>
            </div>
          </div>
        </div>
      </el-aside>

      <!-- Main Content -->
      <el-main class="app-main">
        <div class="main-content-wrapper">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.app-container {
  height: 100vh;
  background: var(--pv-bg);
}

/* Header */
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--pv-space-6);
  height: 60px;
  border-bottom: 1px solid var(--pv-border-light);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
}

.app-logo {
  display: flex;
  align-items: center;
  gap: var(--pv-space-2);
  cursor: pointer;
}

.logo-icon {
  color: var(--pv-primary);
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: var(--pv-text);
  letter-spacing: -0.5px;
}

.logo-suffix {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--pv-primary), var(--pv-accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Navigation */
.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: var(--pv-space-1);
  background: var(--pv-bg);
  padding: var(--pv-space-1);
  border-radius: var(--pv-radius-lg);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--pv-space-2);
  padding: var(--pv-space-2) var(--pv-space-4);
  border-radius: var(--pv-radius);
  color: var(--pv-text-secondary);
  text-decoration: none;
  font-weight: 500;
  font-size: 14px;
  transition: all var(--pv-transition);
  cursor: pointer;
}

.nav-item:hover {
  color: var(--pv-text);
  background: var(--pv-surface);
}

.nav-item.active {
  color: var(--pv-primary);
  background: var(--pv-surface);
  box-shadow: var(--pv-shadow-sm);
}

.header-right {
  display: flex;
  align-items: center;
}

.lang-select {
  width: 120px;
}

.lang-select :deep(.el-input__wrapper) {
  border-radius: var(--pv-radius);
  background: var(--pv-bg);
}

/* Sidebar */
.main-container {
  height: calc(100vh - 60px);
}

.app-sidebar {
  background: var(--pv-surface);
  border-right: 1px solid var(--pv-border-light);
  transition: width var(--pv-transition-slow);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: var(--pv-space-3) var(--pv-space-3);
  border-bottom: 1px solid var(--pv-border-light);
}

.sidebar-toggle {
  width: 36px;
  height: 36px;
  border-radius: var(--pv-radius);
  color: var(--pv-text-secondary);
}

.sidebar-toggle:hover {
  background: var(--pv-surface-hover);
  color: var(--pv-text);
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--pv-space-5);
}

.sidebar-section {
  margin-bottom: var(--pv-space-6);
}

.sidebar-section-title {
  display: flex;
  align-items: center;
  gap: var(--pv-space-2);
  font-size: 13px;
  font-weight: 600;
  color: var(--pv-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--pv-space-4);
}

.sidebar-section-title .el-icon {
  font-size: 16px;
}

/* Config Card */
.config-card {
  background: var(--pv-bg);
  border-radius: var(--pv-radius);
  padding: var(--pv-space-4);
}

.config-group {
  margin-bottom: var(--pv-space-3);
}

.config-label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--pv-text-secondary);
  margin-bottom: var(--pv-space-1);
}

.config-group :deep(.el-input__wrapper) {
  background: var(--pv-surface);
}

.save-btn {
  width: 100%;
  margin-top: var(--pv-space-3);
}

/* Main Content */
.app-main {
  background: var(--pv-bg);
  padding: var(--pv-space-6);
  overflow-y: auto;
}

.main-content-wrapper {
  max-width: 1440px;
  margin: 0 auto;
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
