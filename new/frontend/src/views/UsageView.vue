<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import {
  TrendCharts,
  Coin,
  Cpu,
  SuccessFilled,
  CircleCloseFilled,
  Timer,
} from '@element-plus/icons-vue'
import {
  getUsageSummary,
  getUsageRecords,
  type UsageSummary,
  type UsageRecord,
  type UsageSummaryByModel,
} from '@/api/usage'

const { t } = useI18n()

const loading = ref(false)
const summary = ref<UsageSummary | null>(null)
const records = ref<UsageRecord[]>([])
const recordsTotal = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const selectedDays = ref(30)
const selectedService = ref('')
const selectedModel = ref('')

const dayOptions = [
  { label: '7 ' + t('usage.days_unit'), value: 7 },
  { label: '30 ' + t('usage.days_unit'), value: 30 },
  { label: '90 ' + t('usage.days_unit'), value: 90 },
  { label: '365 ' + t('usage.days_unit'), value: 365 },
]

const serviceOptions = computed(() => {
  if (!summary.value) return []
  return Object.keys(summary.value.by_service).map(s => ({ label: s.toUpperCase(), value: s }))
})

const modelOptions = computed(() => {
  if (!summary.value) return []
  return Object.keys(summary.value.by_model).map(m => ({ label: m, value: m }))
})

// Sorted by_date for chart
const chartDates = computed(() => {
  if (!summary.value?.by_date) return []
  return Object.keys(summary.value.by_date).sort()
})

const chartCallsData = computed(() =>
  chartDates.value.map(d => summary.value!.by_date[d].calls)
)

const chartCostData = computed(() =>
  chartDates.value.map(d => Number(summary.value!.by_date[d].cost.toFixed(4)))
)

// Sorted by_model for table
const modelBreakdown = computed(() => {
  if (!summary.value?.by_model) return []
  return Object.entries<UsageSummaryByModel>(summary.value.by_model)
    .map(([model, data]) => ({ model, ...data }))
    .sort((a, b) => b.calls - a.calls)
})

const maxChartCalls = computed(() => Math.max(...(chartCallsData.value.length ? chartCallsData.value : [1])))

async function loadSummary() {
  try {
    const res = await getUsageSummary(selectedDays.value)
    summary.value = res.data
  } catch (e: any) {
    ElMessage.error(t('usage.load_failed'))
  }
}

async function loadRecords() {
  loading.value = true
  try {
    const res = await getUsageRecords({
      service: selectedService.value || undefined,
      model: selectedModel.value || undefined,
      days: selectedDays.value,
      page: currentPage.value,
      page_size: pageSize.value,
    })
    records.value = res.records
    recordsTotal.value = res.total
  } catch (e: any) {
    ElMessage.error(t('usage.load_failed'))
  } finally {
    loading.value = false
  }
}

async function refresh() {
  loading.value = true
  await Promise.all([loadSummary(), loadRecords()])
  loading.value = false
}

function formatCost(cost: number) {
  if (cost < 0.01) return `$${cost.toFixed(4)}`
  return `$${cost.toFixed(2)}`
}

function formatTokens(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return String(n)
}

function formatDate(ts: string) {
  return ts.replace('T', ' ').slice(0, 19)
}

onMounted(refresh)
</script>

<template>
  <div class="usage-view">
    <header class="usage-header">
      <div>
        <h2>{{ t('usage.title') }}</h2>
        <p class="subtitle">{{ t('usage.subtitle') }}</p>
      </div>
      <div class="header-controls">
        <el-select v-model="selectedDays" size="default" style="width: 130px" @change="refresh">
          <el-option v-for="opt in dayOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
        </el-select>
        <el-button type="primary" :icon="TrendCharts" @click="refresh" :loading="loading">
          {{ t('usage.refresh') }}
        </el-button>
      </div>
    </header>

    <!-- Summary cards -->
    <div v-if="summary" class="summary-cards">
      <div class="stat-card">
        <div class="stat-icon" style="background: #eef2ff;"><el-icon :size="22" color="#4f46e5"><Cpu /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ summary.total_calls }}</span>
          <span class="stat-label">{{ t('usage.total_calls') }}</span>
        </div>
        <div class="stat-badge-group">
          <span class="badge badge-success"><el-icon><SuccessFilled /></el-icon>{{ summary.success_count }}</span>
          <span v-if="summary.fail_count" class="badge badge-fail"><el-icon><CircleCloseFilled /></el-icon>{{ summary.fail_count }}</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background: #f0fdf4;"><el-icon :size="22" color="#16a34a"><Coin /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ formatCost(summary.total_cost) }}</span>
          <span class="stat-label">{{ t('usage.total_cost') }}</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background: #eff6ff;"><el-icon :size="22" color="#2563eb"><Timer /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ formatTokens(summary.total_input_tokens + summary.total_output_tokens) }}</span>
          <span class="stat-label">{{ t('usage.total_tokens') }}</span>
        </div>
        <div class="stat-detail">
          <span>{{ t('usage.input') }}: {{ formatTokens(summary.total_input_tokens) }}</span>
          <span>{{ t('usage.output') }}: {{ formatTokens(summary.total_output_tokens) }}</span>
        </div>
      </div>
    </div>

    <!-- Chart area -->
    <div v-if="summary && chartDates.length" class="chart-section">
      <div class="section-header">
        <h3>{{ t('usage.trend') }}</h3>
        <div class="chart-legend">
          <span class="legend-item"><i class="legend-dot" style="background:#6366f1"></i>{{ t('usage.calls') }}</span>
          <span class="legend-item"><i class="legend-dot" style="background:#f59e0b"></i>{{ t('usage.cost') }} ($)</span>
        </div>
      </div>
      <div class="bar-chart">
        <div v-for="(date, i) in chartDates" :key="date" class="bar-group">
          <div class="bar-pair">
            <div
              class="bar bar-calls"
              :style="{ height: (chartCallsData[i] / maxChartCalls * 100) + '%' }"
              :title="chartCallsData[i] + ' calls'"
            ></div>
            <div
              class="bar bar-cost"
              :style="{ height: Math.max(chartCostData[i] / Math.max(...(chartCostData.length ? chartCostData : [1])) * 100, 2) + '%' }"
              :title="'$' + chartCostData[i]"
            ></div>
          </div>
          <span class="bar-label">{{ date.slice(5) }}</span>
        </div>
      </div>
    </div>

    <!-- Model breakdown -->
    <div v-if="modelBreakdown.length" class="model-section">
      <h3>{{ t('usage.model_breakdown') }}</h3>
      <div class="model-table-wrap">
        <table class="model-table">
          <thead>
            <tr>
              <th>{{ t('usage.model') }}</th>
              <th>{{ t('usage.service') }}</th>
              <th>{{ t('usage.calls') }}</th>
              <th>{{ t('usage.input_tokens') }}</th>
              <th>{{ t('usage.output_tokens') }}</th>
              <th>{{ t('usage.cost') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in modelBreakdown" :key="row.model">
              <td><code>{{ row.model }}</code></td>
              <td><el-tag size="small" :type="row.service === 'llm' ? 'primary' : 'success'">{{ row.service }}</el-tag></td>
              <td>{{ row.calls }}</td>
              <td>{{ formatTokens(row.input_tokens) }}</td>
              <td>{{ formatTokens(row.output_tokens) }}</td>
              <td>{{ formatCost(row.cost) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Records table -->
    <div class="records-section">
      <div class="section-header">
        <h3>{{ t('usage.records') }}</h3>
        <div class="filter-group">
          <el-select v-model="selectedService" clearable :placeholder="t('usage.filter_service')" size="small" style="width: 120px" @change="() => { currentPage = 1; loadRecords() }">
            <el-option v-for="opt in serviceOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
          <el-select v-model="selectedModel" clearable :placeholder="t('usage.filter_model')" size="small" style="width: 180px" @change="() => { currentPage = 1; loadRecords() }">
            <el-option v-for="opt in modelOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </div>
      </div>

      <el-table :data="records" stripe size="small" v-loading="loading" class="records-table">
        <el-table-column prop="timestamp" :label="t('usage.time')" width="170">
          <template #default="{ row }">{{ formatDate(row.timestamp) }}</template>
        </el-table-column>
        <el-table-column prop="service" :label="t('usage.service')" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="row.service === 'llm' ? 'primary' : 'success'">{{ row.service }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="model" :label="t('usage.model')" min-width="150">
          <template #default="{ row }"><code>{{ row.model }}</code></template>
        </el-table-column>
        <el-table-column prop="action" :label="t('usage.action')" width="90" />
        <el-table-column prop="input_tokens" :label="t('usage.input_tokens')" width="100" align="right">
          <template #default="{ row }">{{ formatTokens(row.input_tokens) }}</template>
        </el-table-column>
        <el-table-column prop="output_tokens" :label="t('usage.output_tokens')" width="100" align="right">
          <template #default="{ row }">{{ formatTokens(row.output_tokens) }}</template>
        </el-table-column>
        <el-table-column prop="cost" :label="t('usage.cost')" width="90" align="right">
          <template #default="{ row }">{{ formatCost(row.cost) }}</template>
        </el-table-column>
        <el-table-column prop="success" :label="t('usage.status')" width="80" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.success" color="#16a34a"><SuccessFilled /></el-icon>
            <el-icon v-else color="#dc2626"><CircleCloseFilled /></el-icon>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="recordsTotal > pageSize" class="pagination-wrap">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="recordsTotal"
          layout="prev, pager, next"
          size="small"
          @current-change="loadRecords"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.usage-view {
  max-width: 1080px;
  margin: 0 auto;
  padding: 28px 32px;
  overflow-y: auto;
  height: 100%;
}

.usage-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
}

.usage-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.subtitle {
  margin: 4px 0 0;
  font-size: 13px;
  color: #9ca3af;
}

.header-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

/* Summary cards */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 18px 20px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 14px;
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #111827;
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  color: #9ca3af;
}

.stat-badge-group {
  display: flex;
  gap: 6px;
  margin-left: auto;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
}

.badge-success {
  color: #16a34a;
  background: #f0fdf4;
}

.badge-fail {
  color: #dc2626;
  background: #fef2f2;
}

.stat-detail {
  width: 100%;
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #9ca3af;
  padding-top: 4px;
}

/* Chart */
.chart-section {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 20px;
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.chart-legend {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #9ca3af;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 2px;
  display: inline-block;
}

.bar-chart {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 120px;
  padding-top: 8px;
  overflow-x: auto;
}

.bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  min-width: 28px;
}

.bar-pair {
  display: flex;
  gap: 2px;
  align-items: flex-end;
  height: 100px;
  width: 100%;
}

.bar {
  flex: 1;
  border-radius: 3px 3px 0 0;
  min-height: 2px;
  transition: height 0.3s ease;
}

.bar-calls {
  background: #6366f1;
}

.bar-cost {
  background: #f59e0b;
}

.bar-label {
  font-size: 10px;
  color: #9ca3af;
  margin-top: 4px;
  white-space: nowrap;
}

/* Model breakdown */
.model-section {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 20px;
  margin-bottom: 24px;
}

.model-section h3 {
  font-size: 15px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 14px;
}

.model-table-wrap {
  overflow-x: auto;
}

.model-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.model-table th,
.model-table td {
  text-align: left;
  padding: 8px 12px;
  border-bottom: 1px solid #f3f4f6;
}

.model-table th {
  color: #6b7280;
  font-weight: 500;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.model-table td {
  color: #374151;
}

.model-table code {
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

/* Records */
.records-section {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 20px;
}

.filter-group {
  display: flex;
  gap: 8px;
}

.records-table {
  width: 100%;
}

.records-table code {
  background: #f3f4f6;
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 12px;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 14px;
}

@media (max-width: 720px) {
  .usage-view {
    padding: 16px;
  }

  .summary-cards {
    grid-template-columns: 1fr;
  }

  .usage-header {
    flex-direction: column;
    gap: 12px;
  }

  .header-controls {
    width: 100%;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
