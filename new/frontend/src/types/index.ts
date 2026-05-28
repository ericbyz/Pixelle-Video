// ============================================================
// Pipeline types
// ============================================================

export type PipelineType =
  | 'quick_create'
  | 'custom_media'
  | 'digital_human'
  | 'image_to_video'
  | 'action_transfer'

export interface PipelineInfo {
  key: PipelineType
  name: string
  description: string
  icon: string
}

// ============================================================
// Video generation
// ============================================================

export type VideoMode = 'generate' | 'fixed'

export interface VideoGenerateRequest {
  text: string
  mode: VideoMode
  title?: string
  n_scenes?: number
  tts_workflow?: string
  ref_audio?: string
  voice_id?: string
  min_narration_words?: number
  max_narration_words?: number
  min_image_prompt_words?: number
  max_image_prompt_words?: number
  media_workflow?: string
  video_fps?: number
  frame_template?: string
  template_params?: Record<string, any>
  prompt_prefix?: string
  bgm_path?: string
  bgm_volume?: number
}

export interface VideoGenerateResponse {
  success: boolean
  message: string
  video_url: string
  duration: number
  file_size: number
}

export interface VideoGenerateAsyncResponse {
  success: boolean
  message: string
  task_id: string
}

// ============================================================
// Resources
// ============================================================

export interface WorkflowInfo {
  name: string
  display_name: string
  source: string
  path: string
  key: string
  workflow_id?: string
}

export interface WorkflowListResponse {
  workflows: WorkflowInfo[]
}

export interface TemplateInfo {
  name: string
  display_name: string
  size: string
  width: number
  height: number
  orientation: string
  path: string
  key: string
}

export interface TemplateListResponse {
  templates: TemplateInfo[]
}

export interface TemplateParamInfo {
  type: string
  default: string
  label: string
}

export interface TemplateParamsResponse {
  template: string
  media_width: number
  media_height: number
  params: Record<string, TemplateParamInfo>
}

export interface BGMInfo {
  name: string
  path: string
  source: string
}

export interface BGMListResponse {
  bgm_files: BGMInfo[]
}

// ============================================================
// Tasks
// ============================================================

export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
export type TaskType = 'video_generation'

export interface TaskProgress {
  current: number
  total: number
  percentage: number
  message: string
}

export interface Task {
  task_id: string
  task_type: TaskType
  status: TaskStatus
  progress: TaskProgress | null
  result: any | null
  error: string | null
  created_at: string
  started_at: string | null
  completed_at: string | null
  request_params: Record<string, any> | null
}

// ============================================================
// Config
// ============================================================

export interface LLMConfig {
  api_key: string
  base_url: string
  model: string
}

export interface ComfyUIConfig {
  comfyui_url: string
  comfyui_api_key: string
  runninghub_api_key: string
  runninghub_concurrent_limit: number
  runninghub_instance_type: string
}

export interface AppConfig {
  llm: LLMConfig
  comfyui: ComfyUIConfig
}

// ============================================================
// Content generation
// ============================================================

export interface NarrationGenerateRequest {
  text: string
  n_scenes: number
  min_words?: number
  max_words?: number
}

export interface NarrationGenerateResponse {
  narrations: string[]
}

export interface TitleGenerateRequest {
  text: string
  style?: string
}

export interface TitleGenerateResponse {
  title: string
}

// ============================================================
// TTS
// ============================================================

export interface TTSRequest {
  text: string
  workflow?: string
  ref_audio?: string
  voice_id?: string
}

export interface TTSResponse {
  audio_path: string
  duration: number
}

// ============================================================
// Image
// ============================================================

export interface ImageGenerateRequest {
  prompt: string
  width?: number
  height?: number
  workflow?: string
}

export interface ImageGenerateResponse {
  image_path: string
}

// ============================================================
// Frame
// ============================================================

export interface FrameRenderRequest {
  template: string
  title?: string
  text?: string
  image?: string
}

export interface FrameRenderResponse {
  frame_path: string
  width: number
  height: number
}

// ============================================================
// API base response
// ============================================================

export interface BaseResponse<T = any> {
  success: boolean
  message: string
  data?: T
}

// ============================================================
// WebSocket progress events
// ============================================================

export interface ProgressEvent {
  type: 'progress' | 'status' | 'error' | 'complete'
  task_id: string
  data: {
    current?: number
    total?: number
    percentage?: number
    message?: string
    error?: string
    result?: any
  }
}
