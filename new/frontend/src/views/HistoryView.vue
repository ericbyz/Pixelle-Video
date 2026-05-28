<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Clock,
  Delete,
  Download,
  View,
  Search,
  Refresh,
  CircleCheck,
  CircleClose,
  Loading,
  VideoCamera,
  Timer,
  Document,
} from '@element-plus/icons-vue'
import { useHistoryStore } from '@/stores/history'
import type { Task, TaskStatus } from '@/types'

const { t } = useI18n()
const store = useHistoryStore()

// Status config
const statusConfig: Record<string, { type: string; icon: any; color: string }> = {
  pending: { type: 'info', icon: Clock, color: '#909399' },
  running: { type: 'warning', icon: Loading, color: '#e6a23c' },
  completed: { type: 'success', icon: CircleCheck, color: '#67c23a' },
  failed: { type: 'danger', icon: CircleClose, color: '#f56c6c' },
  cancelled: { type: 'info', icon: CircleClose, color: '#909399' },
}

const statusLabel: Record<string, string> = {
  pending: t('history.status_pending'),
  running: t('history.status_running'),
  completed: t('history.task_card.status_completed'),
  failed: t('history.task_card.status_failed'),
  cancelled: t('history.task_card.status_failed'),
}

// Detail dialog
const detailVisible = ref(false)
const detailTask = ref<Task | null>(null)

const viewDetail = async (taskId: string) => {
  try {
    detailTask.value = await store.fetchTaskDetail(taskId)
    detailVisible.value = true
  } catch {
    ElMessage.error('Failed to load task detail')
  }
}

const handleDelete = async (taskId: string) => {
  try {
    await ElMessageBox.confirm(t('history.action.delete_confirm'), {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消',
    })
    await store.removeTask(taskId)
    ElMessage.success(t('history.action.delete_success'))
  } catch {
    // cancelled or failed
  }
}

const formatTime = (isoStr: string | null) => {
  if (!isoStr) return '-'
  const date = new Date(isoStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  // Less than 1 minute
  if (diff < 60000) return '刚刚'
  // Less than 1 hour
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  // Less than 24 hours
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  // Otherwise
  return date.toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatDuration = (seconds: number | null) => {
  if (!seconds) return '-'
  if (seconds < 60) return `${Math.round(seconds)}s`
  const mins = Math.floor(seconds / 60)
  const secs = Math.round(seconds % 60)
  return `${mins}m ${secs}s`
}

const getVideoUrl = (task: Task) => {
  if (task.result?.video_url) return task.result.video_url
  return ''
}

onMounted(() => {
  store.fetchTasks()
})

const openUrl = (url: string) => {
  window.open(url, '_blank')
}
</script>

<template>
  <div class="history-view animate-fade-in">
    <!-- Header Section -->
    <div class="history-header">
      <div class="header-info">
        <h1 class="page-title">
          <el-icon><Clock /></el-icon>
          {{ t('history.page_title') }}
        </h1>
        <p class="page-subtitle">查看和管理您的视频生成记录</p>
      </div>

      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon total">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ store.totalCount }}</span>
            <span class="stat-label">{{ t('history.total_tasks') }}</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon success">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ store.completedCount }}</span>
            <span class="stat-label">{{ t('history.completed_count') }}</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon danger">
            <el-icon><CircleClose /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ store.failedCount }}</span>
            <span class="stat-label">{{ t('history.failed_count') }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-section">
      <div class="filter-bar">
        <div class="filter-left">
          <el-select
            v-model="store.filterStatus"
            :placeholder="t('history.filter_status')"
            clearable
            class="status-filter"
          >
            <el-option :label="t('history.status_all')" value="" />
            <el-option :label="t('history.status_completed')" value="completed" />
            <el-option :label="t('history.status_failed')" value="failed" />
            <el-option :label="t('history.status_running')" value="running" />
            <el-option :label="t('history.status_pending')" value="pending" />
          </el-select>
        </div>

        <el-button
          :icon="Refresh"
          circle
          @click="store.fetchTasks()"
          :loading="store.isLoading"
        />
      </div>
    </div>

    <!-- Task List -->
    <div class="task-list-section">
      <!-- Empty State -->
      <div v-if="store.pagedTasks.length === 0" class="empty-state">
        <div class="empty-icon">
          <el-icon :size="64"><VideoCamera /></el-icon>
        </div>
        <h3 class="empty-title">{{ t('history.no_tasks') }}</h3>
        <p class="empty-desc">开始创建您的第一个视频吧</p>
      </div>

      <!-- Task Cards -->
      <div v-else class="task-grid">
        <div
          v-for="task in store.pagedTasks"
          :key="task.task_id"
          class="task-card"
          :class="{ 'is-completed': task.status === 'completed' }"
        >
          <!-- Status Indicator -->
          <div
            class="task-status-bar"
            :style="{ background: statusConfig[task.status]?.color }"
          />

          <div class="task-card-body">
            <!-- Header -->
            <div class="task-header">
              <div class="task-id-wrapper">
                <span class="task-id">#{{ task.task_id.slice(0, 8) }}</span>
              </div>
              <el-tag
                :type="statusConfig[task.status]?.type as any"
                size="small"
                effect="light"
                round
              >
                <el-icon class="tag-icon">
                  <component :is="statusConfig[task.status]?.icon" />
                </el-icon>
                {{ statusLabel[task.status] }}
              </el-tag>
            </div>

            <!-- Meta Info -->
            <div class="task-meta">
              <div class="meta-item">
                <el-icon><Clock /></el-icon>
                <span>{{ formatTime(task.created_at) }}</span>
              </div>
              <div class="meta-item" v-if="task.request_params?.n_scenes">
                <el-icon><Film /></el-icon>
                <span>{{ task.request_params.n_scenes }} 场景</span>
              </div>
            </div>

            <!-- Preview Text -->
            <div class="task-preview" v-if="task.request_params?.text">
              {{ task.request_params.text.slice(0, 80) }}{{ task.request_params.text.length > 80 ? '...' : '' }}
            </div>

            <!-- Progress Bar (for running tasks) -->
            <div class="task-progress" v-if="task.status === 'running' && task.progress">
              <el-progress
                :percentage="task.progress.percentage"
                :stroke-width="6"
                :show-text="false"
              />
              <span class="progress-label">{{ task.progress.message || '处理中...' }}</span>
            </div>

            <!-- Actions -->
            <div class="task-actions">
              <el-button
                size="small"
                :icon="View"
                class="action-btn view-btn"
                @click="viewDetail(task.task_id)"
              >
                {{ t('history.task_card.view_detail') }}
              </el-button>

              <el-button
                v-if="task.status === 'completed' && getVideoUrl(task)"
                size="small"
                type="primary"
                :icon="Download"
                class="action-btn download-btn"
                @click="() => openUrl(getVideoUrl(task))"
              >
                {{ t('history.task_card.download') }}
              </el-button>

              <el-button
                size="small"
                type="danger"
                :icon="Delete"
                class="action-btn delete-btn"
                plain
                @click="handleDelete(task.task_id)"
              >
                {{ t('history.task_card.delete') }}
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination-section" v-if="store.totalCount > 0">
      <el-pagination
        v-model:current-page="store.currentPage"
        v-model:page-size="store.pageSize"
        :total="store.totalCount"
        :page-sizes="[6, 12, 24, 48]"
        layout="total, sizes, prev, pager, next"
        background
      />
    </div>

    <!-- Detail Dialog -->
    <el-dialog
      v-model="detailVisible"
      :title="t('history.detail.modal_title')"
      width="800px"
      class="detail-dialog"
      destroy-on-close
    >
      <template v-if="detailTask">
        <div class="detail-content">
          <!-- Status Banner -->
          <div
            class="detail-status-banner"
            :style="{ background: statusConfig[detailTask.status]?.color }"
          >
            <el-icon :size="24">
              <component :is="statusConfig[detailTask.status]?.icon" />
            </el-icon>
            <span>{{ statusLabel[detailTask.status] }}</span>
          </div>

          <!-- Info Grid -->
          <div class="detail-info-grid">
            <div class="info-item">
              <span class="info-label">{{ t('history.detail.task_id') }}</span>
              <span class="info-value mono">{{ detailTask.task_id }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">{{ t('history.task_card.created_at') }}</span>
              <span class="info-value">{{ formatTime(detailTask.created_at) }}</span>
            </div>
            <div class="info-item" v-if="detailTask.completed_at">
              <span class="info-label">{{ t('history.sort_completed_at') }}</span>
              <span class="info-value">{{ formatTime(detailTask.completed_at) }}</span>
            </div>
            <div class="info-item" v-if="detailTask.request_params?.mode">
              <span class="info-label">{{ t('history.detail.mode') }}</span>
              <span class="info-value">{{ detailTask.request_params.mode }}</span>
            </div>
          </div>

          <!-- Input Text -->
          <div class="detail-section" v-if="detailTask.request_params?.text">
            <h4 class="section-title">{{ t('history.detail.input_params') }}</h4>
            <div class="text-preview">
              {{ detailTask.request_params.text }}
            </div>
          </div>

          <!-- Error -->
          <div class="detail-error" v-if="detailTask.error">
            <el-alert
              :title="detailTask.error"
              type="error"
              show-icon
              :closable="false"
            />
          </div>

          <!-- Video Result -->
          <div class="detail-section" v-if="detailTask.result?.video_url">
            <h4 class="section-title">{{ t('history.detail.download_video') }}</h4>
            <div class="video-preview">
              <video
                :src="detailTask.result.video_url"
                controls
                class="video-player"
              />
            </div>
            <el-button
              type="primary"
              :icon="Download"
              @click="() => openUrl(detailTask!.result!.video_url!)"
              class="download-action"
            >
              {{ t('history.detail.download_video') }}
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.history-view {
  padding-bottom: var(--pv-space-10);
}

/* Header */
.history-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--pv-space-6);
  flex-wrap: wrap;
  gap: var(--pv-space-6);
}

.header-info {
  flex: 1;
}

.page-title {
  display: flex;
  align-items: center;
  gap: var(--pv-space-3);
  font-size: 24px;
  font-weight: 700;
  color: var(--pv-text);
  margin-bottom: var(--pv-space-2);
}

.page-title .el-icon {
  color: var(--pv-primary);
}

.page-subtitle {
  font-size: 14px;
  color: var(--pv-text-secondary);
}

/* Stats Grid */
.stats-grid {
  display: flex;
  gap: var(--pv-space-4);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--pv-space-3);
  padding: var(--pv-space-4) var(--pv-space-5);
  background: var(--pv-surface);
  border: 1px solid var(--pv-border-light);
  border-radius: var(--pv-radius-lg);
  min-width: 140px;
}

.stat-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--pv-radius);
  font-size: 20px;
}

.stat-icon.total {
  background: var(--pv-primary-100);
  color: var(--pv-primary);
}

.stat-icon.success {
  background: #d1fae5;
  color: #059669;
}

.stat-icon.danger {
  background: #fee2e2;
  color: #dc2626;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--pv-text);
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  color: var(--pv-text-secondary);
}

/* Filter Section */
.filter-section {
  margin-bottom: var(--pv-space-5);
}

.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--pv-space-4);
}

.filter-left {
  display: flex;
  align-items: center;
  gap: var(--pv-space-3);
}

.status-filter {
  width: 200px;
}

/* Task Grid */
.task-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: var(--pv-space-4);
}

/* Task Card */
.task-card {
  position: relative;
  background: var(--pv-surface);
  border: 1px solid var(--pv-border-light);
  border-radius: var(--pv-radius-lg);
  overflow: hidden;
  transition: all var(--pv-transition);
}

.task-card:hover {
  box-shadow: var(--pv-shadow-lg);
  border-color: var(--pv-border);
  transform: translateY(-2px);
}

.task-card.is-completed {
  border-color: #d1fae5;
}

.task-status-bar {
  height: 3px;
  width: 100%;
}

.task-card-body {
  padding: var(--pv-space-5);
}

.task-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--pv-space-3);
}

.task-id-wrapper {
  display: flex;
  align-items: center;
  gap: var(--pv-space-2);
}

.task-id {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
  font-weight: 600;
  color: var(--pv-text-secondary);
  background: var(--pv-bg);
  padding: 2px 8px;
  border-radius: 4px;
}

.tag-icon {
  margin-right: 4px;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: var(--pv-space-4);
  margin-bottom: var(--pv-space-3);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: var(--pv-space-1);
  font-size: 12px;
  color: var(--pv-text-secondary);
}

.meta-item .el-icon {
  font-size: 14px;
}

.task-preview {
  font-size: 13px;
  color: var(--pv-text-secondary);
  line-height: 1.5;
  margin-bottom: var(--pv-space-4);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.task-progress {
  margin-bottom: var(--pv-space-4);
}

.progress-label {
  display: block;
  font-size: 12px;
  color: var(--pv-text-secondary);
  margin-top: var(--pv-space-2);
}

.task-actions {
  display: flex;
  gap: var(--pv-space-2);
  flex-wrap: wrap;
}

.action-btn {
  flex: 1;
  min-width: 0;
}

.delete-btn {
  flex: 0;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: var(--pv-space-12) var(--pv-space-6);
}

.empty-icon {
  color: var(--pv-text-muted);
  margin-bottom: var(--pv-space-4);
  opacity: 0.5;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--pv-text);
  margin-bottom: var(--pv-space-2);
}

.empty-desc {
  font-size: 14px;
  color: var(--pv-text-secondary);
}

/* Pagination */
.pagination-section {
  display: flex;
  justify-content: center;
  margin-top: var(--pv-space-8);
  padding: var(--pv-space-4) 0;
}

/* Detail Dialog */
.detail-dialog :deep(.el-dialog) {
  border-radius: var(--pv-radius-xl);
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: var(--pv-space-5);
}

.detail-status-banner {
  display: flex;
  align-items: center;
  gap: var(--pv-space-3);
  padding: var(--pv-space-4) var(--pv-space-5);
  border-radius: var(--pv-radius);
  color: white;
  font-weight: 600;
  font-size: 16px;
}

.detail-info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--pv-space-4);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: var(--pv-space-1);
}

.info-label {
  font-size: 12px;
  color: var(--pv-text-secondary);
  font-weight: 500;
}

.info-value {
  font-size: 14px;
  color: var(--pv-text);
  font-weight: 500;
}

.info-value.mono {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
}

.detail-section {
  margin-top: var(--pv-space-2);
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--pv-text);
  margin-bottom: var(--pv-space-3);
}

.text-preview {
  background: var(--pv-bg);
  padding: var(--pv-space-4);
  border-radius: var(--pv-radius);
  font-size: 14px;
  line-height: 1.6;
  color: var(--pv-text);
  max-height: 200px;
  overflow-y: auto;
}

.detail-error {
  margin-top: var(--pv-space-2);
}

.video-preview {
  margin-bottom: var(--pv-space-4);
}

.video-player {
  width: 100%;
  max-height: 400px;
  border-radius: var(--pv-radius);
  background: #000;
}

.download-action {
  width: 100%;
}
</style>
