<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import {
  HomeFilled,
  Clock,
  Setting,
  VideoCamera,
} from '@element-plus/icons-vue'

const { t, locale } = useI18n()
const router = useRouter()

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
</script>

<template>
  <el-container class="app-container">
    <!-- Top Navigation Bar -->
    <el-header class="app-header glass">
      <div class="header-left">
        <div class="app-logo" @click="router.push('/home')">
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
          <router-link
            to="/settings"
            class="nav-item"
            :class="{ active: activeMenu === '/settings' }"
          >
            <el-icon><Setting /></el-icon>
            <span>{{ t('nav.settings') || '设置' }}</span>
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

/* Main Content */
.app-main {
  background: var(--pv-bg);
  padding: var(--pv-space-6);
  overflow-y: auto;
  height: calc(100vh - 60px);
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
