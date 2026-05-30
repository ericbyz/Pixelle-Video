# Pixelle-Video 前后端视频 API 改造计划

## 1. 背景与目标

当前项目已经拆分为 `old/` 和 `new/`：

- `old/` 是遗留单体项目，只作为参考，不再修改。
- `new/` 是当前活跃项目，采用 FastAPI + Vue 3 + TypeScript。

现状是 `new/backend/main.py` 仍然通过 `sys.path` 和 `os.chdir()` 复用 `old/api` 与 `old/pixelle_video`，前端也已经做出了 5 条视频流程入口，但后端 API 目前只真正支持：

- `standard`：快速创建/标准视频生成。
- `asset_based`：自定义素材生成。

前端已经预留但暂未真正打通的流程：

- `digital_human`
- `image_to_video`
- `action_transfer`

本次改造目标：

1. 保留 old 中已经可用的核心功能与用户工作流。
2. 在 `new/` 中重新设计清晰的前后端 API 边界。
3. 将视频生成相关能力统一成可扩展的视频 API 层。
4. 把“视频 API”和“图片 API”作为与 RunningHub 同级的生成厂家/通道选择，而不是附属配置；用户应能在保留 old 工作流的同时选择 API 通道。
5. 让前端不再靠硬编码和临时拦截适配后端，而是基于后端能力发现、类型契约和任务状态驱动 UI。
6. 改造只发生在 `new/`，`old/` 继续作为参考与兼容依赖，直到功能完全迁移完毕。

## 2. 现状问题

### 2.1 后端问题

`new/backend/main.py` 当前直接引入 `old/api.routers`，并切换工作目录到 `old/`。这能快速启动新前端，但会带来几个问题：

- `new/backend` 没有真正拥有视频 API 的业务边界。
- 路由、Schema、任务管理、文件服务混用 `old/api` 和 `new/backend/routers`。
- 视频 API 只在 `old/api/routers/video.py` 中做了 `standard` 和 `asset_based` 参数构建。
- `VideoGenerateRequest` 虽然接收 `digital_human`、`image_to_video`、`action_transfer` 字段，但 `build_video_params()` 会直接拒绝这些 pipeline。
- old Streamlit 里的 `digital_human`、`image_to_video`、`action_transfer` 逻辑是 UI 内联实现，不是可复用后端服务。

### 2.2 前端问题

`new/frontend/src/views/HomeView.vue` 已经提供 5 条流程入口，但存在以下不匹配：

- `digital_human`、`image_to_video`、`action_transfer` 前端收集了参数，却在提交前被硬拦截。
- `PipelineType` 与后端 `pipeline` 字段不是一一对应，需要手动映射。
- 单个 `HomeView.vue` 同时承载流程选择、上传、TTS 配置、生成、轮询和结果展示，后续扩展会越来越重。
- API 客户端比较薄，缺少统一错误模型、能力发现、请求校验和任务生命周期封装。
- 前端并不知道后端当前支持哪些 pipeline，只能靠写死判断。

## 3. 改造原则

1. `old/` 只读参考，不修改。
2. 新增和重构代码全部放在 `new/`。
3. 先保留兼容，再逐步替换；不要一次性推翻可运行路径。
4. 后端先定义稳定契约，前端再围绕契约重构。
5. 每条视频流程都使用统一任务模型：提交任务、查询进度、获取结果、失败重试/提示。
6. 上传文件统一返回可传给后端 pipeline 的内部路径，同时返回可预览 URL。
7. 前端不硬编码后端能力，改为调用能力发现接口。
8. 生成通道模型必须区分 `runninghub`、`selfhost`、`image_api`、`video_api`；其中 `image_api` 和 `video_api` 语义上等同于厂家选择，使用设置页配置的图片/视频服务。

## 4. 目标架构

### 4.1 后端模块

建议在 `new/backend` 增加以下结构：

```text
new/backend/
  main.py
  core/
    compat.py              # old core 初始化与路径兼容
    files.py               # 文件路径、URL、下载与安全访问
    task_runner.py          # 统一任务执行封装
  schemas/
    video.py               # 视频请求/响应契约
    pipeline.py            # pipeline 能力与表单描述
  services/
    video/
      base.py              # PipelineService 协议
      registry.py          # pipeline 注册表
      standard.py
      asset_based.py
      image_to_video.py
      action_transfer.py
      digital_human.py
      workflow_executor.py # ComfyKit/RunningHub/Selfhost 通用执行器
  routers/
    video.py
    pipelines.py
    tasks.py               # 后续替代 old tasks router
    files.py               # 后续替代 old files router
```

第一阶段可以继续复用 `old/pixelle_video` 的服务实例，但所有新视频 API 入口应迁移到 `new/backend/routers/video.py` 和 `new/backend/services/video/*`。

### 4.2 前端模块

建议重构为：

```text
new/frontend/src/
  api/
    client.ts
    video.ts
    pipelines.ts
    tasks.ts
    upload.ts
  stores/
    generation.ts          # 任务生命周期
    pipeline.ts            # 当前流程与表单状态
  views/
    HomeView.vue
  components/
    pipeline/
      PipelineSelector.vue
      GeneratePanel.vue
      ResultPreview.vue
      StandardForm.vue
      AssetBasedForm.vue
      ImageToVideoForm.vue
      ActionTransferForm.vue
      DigitalHumanForm.vue
      TTSConfig.vue
      WorkflowSelect.vue
```

`HomeView.vue` 只负责组合页面，不再承载所有业务逻辑。

## 5. API 契约设计

### 5.1 能力发现

新增：

```http
GET /api/pipelines
```

响应示例：

```json
{
  "pipelines": [
    {
      "key": "standard",
      "display_name": "快速创建",
      "enabled": true,
      "supports_sync": true,
      "supports_async": true,
      "required_assets": [],
      "workflow_prefixes": ["image_", "video_"]
    },
    {
      "key": "image_to_video",
      "display_name": "图生视频",
      "enabled": true,
      "supports_sync": false,
      "supports_async": true,
      "required_assets": ["image"],
      "workflow_prefixes": ["i2v_"]
    },
    {
      "key": "video_api",
      "display_name": "视频 API",
      "enabled": true,
      "supports_sync": false,
      "supports_async": true,
      "required_assets": [],
      "provider_config": "video_service"
    }
  ]
}
```

前端用该接口决定：

- 哪些流程可点击。
- 哪些流程显示“即将支持”。
- 每条流程应加载哪些工作流。
- 当前流程必须上传哪些素材。

### 5.2 视频生成统一入口

保留旧入口并逐步迁移：

```http
POST /api/video/generate/async
POST /api/video/generate/sync
```

请求体统一为：

```json
{
  "pipeline": "image_to_video",
  "input": {
    "text": "镜头缓慢推进，人物微笑看向镜头",
    "title": "产品展示短片"
  },
  "assets": {
    "image": "uploads/images/xxx.png",
    "video": "uploads/videos/xxx.mp4",
    "character": ["uploads/images/character.png"],
    "goods": ["uploads/images/goods.png"],
    "ref_audio": "uploads/audios/ref.wav"
  },
  "generation": {
    "media_source": "video_api",
    "media_provider": "doubao",
    "media_model": "doubao-seedance-1-0-pro-250428",
    "workflow": null,
    "source": null,
    "duration": 5,
    "fps": 30
  },
  "tts": {
    "mode": "local",
    "voice_id": "zh-CN-YunjianNeural",
    "speed": 1.2,
    "workflow": null,
    "ref_audio": null
  },
  "template": {
    "frame_template": "1080x1920/image_default.html",
    "params": {}
  },
  "audio": {
    "bgm_path": "bgm/default.mp3",
    "bgm_volume": 0.3
  }
}
```

为兼容当前前端和 old API，第一阶段后端可以同时接受旧扁平结构和新结构，并在服务层统一转换成内部 `VideoJobRequest`。

`generation.media_source` 是核心选择字段：

- `runninghub`：使用 old 兼容的 RunningHub 工作流。
- `selfhost`：使用本地 ComfyUI 工作流。
- `image_api`：使用 `image_service` 配置的图片 API 厂家生成图片。
- `video_api`：使用 `video_service` 配置的视频 API 厂家生成视频，产品语义上应与 RunningHub 视频生成能力等价。

当 `media_source` 为 `image_api` 或 `video_api` 时，前端不要求选择 `workflow`；后端应按请求级选择覆盖 old 的全局 provider 推断，避免只能通过全局配置间接切换。
`media_provider` 与 `media_model` 用来表达本次任务选择的具体 API 厂家和模型。

API 通道仍需要具体厂家选择：

- 图片 API：从 `image_service` 预设中选择，例如豆包 SeedDream、通义万相、智谱 CogView 等。
- 视频 API：从 `video_service` 预设中选择，例如豆包 SeedDance、可灵、智谱 CogVideoX 等。
- 创作页可以选择厂家和模型；API Key、Base URL 等敏感配置仍由设置页保存。

### 5.3 任务与进度

继续保留：

```http
GET /api/tasks/{task_id}
DELETE /api/tasks/{task_id}
GET /ws/progress/{task_id}
```

统一任务结果：

```json
{
  "task_id": "xxx",
  "status": "completed",
  "progress": {
    "percentage": 100,
    "message": "完成"
  },
  "result": {
    "video_url": "http://localhost:8000/api/files/output/xxx/final.mp4",
    "video_path": "output/xxx/final.mp4",
    "duration": 12.5,
    "file_size": 12345678,
    "artifacts": []
  },
  "error": null
}
```

## 6. Pipeline 迁移方案

### 6.1 standard

来源：

- `old/api/routers/video.py`
- `old/pixelle_video/pipelines/standard.py`

计划：

1. 把 `build_standard_params()` 从 old router 迁移/重写到 `new/backend/services/video/standard.py`。
2. 保持 `text`、`mode`、`title`、`n_scenes`、`frame_template`、`media_workflow`、`tts_workflow`、`bgm` 等参数兼容。
3. 前端快速创建流程先不大改，只把请求构建迁移到新 `StandardForm` 和统一 submit。

### 6.2 asset_based

来源：

- `old/api/routers/video.py`
- `old/pixelle_video/pipelines/asset_based.py`
- `old/web/pipelines/asset_based.py`

计划：

1. 把 `build_asset_based_params()` 迁移到 `new/backend/services/video/asset_based.py`。
2. 明确 `assets`、`intent`、`video_title`、`duration`、`source` 的校验。
3. 前端保留当前素材上传体验，但将数据归一到统一 `assets` + `generation` 请求结构。

### 6.3 image_to_video

来源：

- `old/web/pipelines/i2v.py`

计划：

1. 新建 `ImageToVideoPipelineService`。
2. 后端接收 `image`、`prompt_text`、`workflow`。
3. 复用 old 中逻辑：
   - 查找 `i2v_*.json` 工作流。
   - 调用 ComfyKit/RunningHub 执行 workflow。
   - 从结果中提取 video URL。
   - 下载到任务目录 `final.mp4`。
4. 新增资源过滤接口或参数：

```http
GET /api/resources/workflows?kind=image_to_video
```

也可以先在现有 `/api/resources/workflows/media` 的基础上前端按 `i2v_` 过滤。

### 6.4 action_transfer

来源：

- `old/web/pipelines/action_transfer.py`

计划：

1. 新建 `ActionTransferPipelineService`。
2. 后端接收 `action_video`、`action_image`、`prompt_text`、`duration`、`workflow`。
3. 复用 old 中逻辑：
   - 查找 `af_*.json` 工作流。
   - 参数映射为 `{ video, image, prompt, second }`。
   - 生成后下载 `final.mp4`。
4. 前端上传动作视频后可读取视频时长，默认 `duration = min(video_duration, 30)`；如果前端不做，后端兜底处理。

### 6.5 digital_human

来源：

- `old/web/pipelines/digital_human.py`

计划：

1. 新建 `DigitalHumanPipelineService`。
2. 支持两个模式：
   - `digital`：人物图 + 商品图 + 商品标题/文案。
   - `customize`：人物图 + 自定义文案。
3. 抽出通用步骤：
   - 合成/生成图片。
   - 生成 TTS 音频。
   - 图片 + 音频生成数字人视频。
   - 下载并返回 `final.mp4`。
4. 工作流路径由 `source` 决定：
   - RunningHub：`digital_image.json`、`digital_combination.json`、`digital_customize.json`
   - Selfhost：同名 selfhost 工作流，如果存在则启用。
5. 前端当前 `digital_human` 表单可以保留，但提交时不再拦截，改为调用后端能力发现判断是否启用。

## 7. 前端重构计划

### 7.1 API 层

1. `api/client.ts` 增加统一错误类型与可选静默错误。
2. `api/video.ts` 提供：
   - `createVideoTask(payload)`
   - `generateVideoSync(payload)`
   - `normalizeLegacyPayload(payload)`
3. `api/pipelines.ts` 提供：
   - `listPipelines()`
   - `listPipelineWorkflows(pipeline)`
4. `api/tasks.ts` 增加任务轮询封装，避免页面内动态 import。

### 7.2 Store 层

1. `pipeline.ts` 只管理当前流程与表单草稿。
2. 新增 `generation.ts` 管理：
   - 当前任务 ID
   - 生成状态
   - 进度
   - 结果
   - 错误
   - 轮询/取消
3. 生成提交逻辑从 `HomeView.vue` 移出。

### 7.3 组件层

优先拆分：

1. `PipelineSelector.vue`
2. `StandardForm.vue`
3. `AssetBasedForm.vue`
4. `ImageToVideoForm.vue`
5. `ActionTransferForm.vue`
6. `DigitalHumanForm.vue`
7. `TTSConfig.vue`
8. `GeneratePanel.vue`
9. `ResultPreview.vue`

拆分后 `HomeView.vue` 只保留页面布局和当前流程组件切换。

### 7.4 UI 行为

1. 如果后端能力发现返回 `enabled=false`，流程卡片可显示禁用状态和原因。
2. 每条 pipeline 独立校验必填项。
3. 文件上传后统一显示：
   - 预览 URL
   - 后端内部 path
   - 类型、大小
4. 所有生成流程统一显示进度、取消、结果预览、打开文件、下载入口。
5. 模板选择必须是可视化图库，不只使用下拉框；至少展示缩略图、方向、尺寸、当前选中状态。
6. 视频/图片/动作迁移相关生成必须支持厂家/通道选择：RunningHub 工作流、本地 Selfhost 工作流、图片 API、视频 API。工作流通道按所选来源过滤；API 通道不展示工作流下拉，而使用设置页的服务配置。
7. 图片 API 和视频 API 通道必须各自支持厂家/模型选择，不能只提供一个模糊的“API”开关。
7. UI 风格参考轻量对话工作台：左侧保持任务输入，右侧集中配置，减少说明性文字，把常用选择做成直接可点的卡片或分段控件。

## 8. 后端重构计划

### 阶段 A：建立 new 后端视频边界

1. 新增 `new/backend/schemas/video.py`。
2. 新增 `new/backend/routers/video.py`。
3. 新增 `new/backend/services/video/registry.py`。
4. `main.py` 先保留 old routers，但视频路由切换为 new router。
5. `standard` 和 `asset_based` 先迁移成功，确保现有前端功能不回退。

验收：

- 快速创建可以生成视频。
- 自定义素材可以生成视频。
- `/api/video/generate/async` 返回任务 ID。
- `/api/tasks/{task_id}` 能拿到结果。

### 阶段 B：接入 image_to_video 与 action_transfer

1. 抽出通用 workflow 执行器。
2. 支持 `i2v_*.json` 工作流发现与执行。
3. 支持 `af_*.json` 工作流发现与执行。
4. 前端取消这两条流程的硬拦截。

验收：

- 图生视频可提交、生成、预览。
- 动作迁移可提交、生成、预览。
- 错误提示能明确显示缺少 workflow、缺少素材、工作流未返回视频等原因。

### 阶段 C：接入 digital_human

1. 迁移 old Streamlit 内联逻辑到 `DigitalHumanPipelineService`。
2. 支持 `digital` 与 `customize` 两种模式。
3. 支持 local TTS 与 comfyui TTS。
4. 前端取消数字人流程硬拦截。

验收：

- 数字人 `digital` 模式可生成。
- 数字人 `customize` 模式可生成。
- 任务结果统一返回 `video_url`。

### 阶段 D：前端组件化与任务体验

1. 拆分 `HomeView.vue`。
2. 引入 `generation` store。
3. 所有流程走统一 submit + task lifecycle。
4. 根据 `/api/pipelines` 控制流程可用状态。

验收：

- 前端代码可维护，单文件体积明显下降。
- 5 条流程使用统一任务体验。
- 不再出现“前端收集了参数但后端暂未开放”的硬编码拦截。

### 阶段 E：逐步移除 old API 路由依赖

1. 将 `tasks`、`files`、`resources`、`config` 按需迁移到 `new/backend`。
2. `main.py` 不再从 `old/api.routers` include router。
3. 只保留对 `old/pixelle_video` 核心服务的兼容调用。
4. 后续再考虑把核心 pipeline 也完全迁移出 `old/`。

验收：

- `new/backend/main.py` 不再 include `old/api.routers`。
- API 文档只反映 new 后端契约。
- old 目录仍未被修改。

## 9. 测试与验证

### 9.1 后端测试

1. Schema 单元测试：
   - 旧扁平 payload 兼容。
   - 新结构 payload 正常解析。
   - 缺少必填素材时返回 400。
2. Pipeline 参数构建测试：
   - `standard`
   - `asset_based`
   - `image_to_video`
   - `action_transfer`
   - `digital_human`
3. Workflow 执行器测试：
   - RunningHub workflow ID。
   - selfhost workflow path。
   - 无视频返回时错误清晰。
4. 文件服务测试：
   - 上传文件可访问。
   - output 文件可访问。
   - 非允许目录不可访问。

### 9.2 前端测试

1. `npm run type-check`
2. `npm run build`
3. 组件级验证：
   - 每条 pipeline 表单必填校验。
   - 上传后预览。
   - 提交 payload 与后端契约一致。
4. 浏览器手动验证：
   - 快速创建。
   - 自定义素材。
   - 图生视频。
   - 动作迁移。
   - 数字人。

## 10. 风险与注意事项

1. old 的 `digital_human`、`image_to_video`、`action_transfer` 逻辑不是服务化实现，迁移时要先抽象通用 workflow executor，避免复制大量 UI 内联代码。
2. `new/backend/main.py` 当前切换工作目录到 `old/`，上传文件会落在 old 工作目录下；需要在文件层明确路径策略，避免前端传入的 `uploads/...` 与 output 路径混乱。
3. 开发桥接后端 `bridge_server.mjs` 不支持 WebSocket，真实进度体验需要直接 FastAPI 模式验证。
4. 视频任务可能很长，前端应优先走 async，不建议依赖 sync。
5. `source=runninghub/selfhost` 与 workflow key 需要统一校验，避免前端选了 selfhost 但后端找不到对应 JSON。
6. 需要保持 old 功能可用，所以第一阶段只替换视频路由，不要同时迁移所有 router。

## 11. 建议实施顺序

1. 先做后端 `standard`、`asset_based` 的 new video router 迁移，保证现有功能不退化。
2. 增加 `/api/pipelines` 能力发现，让前端从硬编码支持状态切换到后端驱动。
3. 做前端 API 层和 generation store，统一任务提交与轮询。
4. 接入 `image_to_video`。
5. 接入 `action_transfer`。
6. 接入 `digital_human`。
7. 拆分 `HomeView.vue`，清理重复表单和硬编码分支。
8. 最后逐步迁移 `tasks/files/resources/config`，减少对 `old/api` 的依赖。

## 12. 第一轮可交付清单

第一轮建议控制范围，目标是“新后端视频边界 + 现有两条流程无回退”：

- `new/backend/schemas/video.py`
- `new/backend/schemas/pipeline.py`
- `new/backend/services/video/base.py`
- `new/backend/services/video/registry.py`
- `new/backend/services/video/standard.py`
- `new/backend/services/video/asset_based.py`
- `new/backend/routers/video.py`
- `new/backend/routers/pipelines.py`
- `new/frontend/src/api/pipelines.ts`
- `new/frontend/src/stores/generation.ts`
- 调整 `new/frontend/src/api/video.ts`
- 小幅调整 `HomeView.vue` 使用新任务提交封装

第一轮完成后，再进入三条新视频 API 的迁移。
