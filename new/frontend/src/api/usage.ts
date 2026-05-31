import apiClient from './client'

// ============================================================
// Types
// ============================================================

export interface UsageSummaryByService {
  calls: number
  input_tokens: number
  output_tokens: number
  cost: number
}

export interface UsageSummaryByModel {
  calls: number
  input_tokens: number
  output_tokens: number
  cost: number
  service: string
}

export interface UsageSummaryByDate {
  calls: number
  cost: number
  input_tokens: number
  output_tokens: number
}

export interface UsageSummary {
  total_calls: number
  success_count: number
  fail_count: number
  total_input_tokens: number
  total_output_tokens: number
  total_cost: number
  by_service: Record<string, UsageSummaryByService>
  by_model: Record<string, UsageSummaryByModel>
  by_date: Record<string, UsageSummaryByDate>
  days: number
}

export interface UsageRecord {
  id: string
  timestamp: string
  service: string
  model: string
  action: string
  input_tokens: number
  output_tokens: number
  cost: number
  success: boolean
  error: string
}

export interface UsageRecordsResponse {
  success: boolean
  records: UsageRecord[]
  total: number
  page: number
  page_size: number
}

export interface UsageModelInfo {
  model: string
  service: string
  input_price: number
  output_price: number
  unit: string
}

export interface UsagePricing {
  [model: string]: {
    input: number
    output: number
    unit: string
  }
}

// ============================================================
// API functions
// ============================================================

export function getUsageSummary(days = 30) {
  return apiClient.get('/usage/summary', { params: { days } }) as unknown as Promise<{
    success: boolean
    data: UsageSummary
  }>
}

export function getUsageRecords(params?: {
  service?: string
  model?: string
  days?: number
  page?: number
  page_size?: number
}) {
  return apiClient.get('/usage/records', { params }) as unknown as Promise<UsageRecordsResponse>
}

export function getUsageModels() {
  return apiClient.get('/usage/models') as unknown as Promise<{
    success: boolean
    models: UsageModelInfo[]
  }>
}

export function getUsagePricing() {
  return apiClient.get('/usage/pricing') as unknown as Promise<{
    success: boolean
    pricing: UsagePricing
  }>
}
