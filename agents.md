# Agents Guide

## 项目结构

本项目包含两个独立的子目录：

| 目录 | 状态 | 说明 |
|------|------|------|
| `new/` | **当前活跃项目** | 前后端分离重构后的版本，所有开发工作在此进行 |
| `old/` | **遗留代码（冻结）** | 旧版单体项目，不再维护 |

## 核心规则

### 任何时候只改 new，不动 old

- 所有新功能、Bug 修复、重构、样式调整等修改，**只能发生在 `new/` 目录下**。
- `old/` 目录仅作参考用途，**严禁修改其中的任何文件**。
- 如果某个功能在 `old/` 中有实现的参考，可以阅读 `old/` 中的代码作为思路借鉴，但最终实现必须写在 `new/` 中。

### 当前项目结构（new/）

```
new/
├── backend/          # Python FastAPI 后端
│   ├── main.py
│   ├── routers/      # API 路由
│   ├── schemas/      # Pydantic 模型
│   └── ...
├── frontend/         # Vue 3 前端（TypeScript）
│   ├── src/
│   │   ├── api/      # API 客户端
│   │   ├── stores/   # Pinia 状态管理
│   │   ├── views/    # 页面组件
│   │   ├── router/   # 路由配置
│   │   ├── i18n/     # 国际化
│   │   └── types/    # 类型定义
│   └── ...
├── start.sh          # 启动脚本
└── package.json      # 项目依赖
```

### 开发约束

1. **代码改动全部限制在 `new/` 内**，不修改 `old/`、`data/`、`output/` 等目录中的任何文件。
2. `old/` 中的代码可读不可写，任何需要从 `old/` 迁移的功能都应重写/适配到 `new/` 的架构中。

## 技术栈（new/）

- **后端**: Python 3.x, FastAPI, Uvicorn
- **前端**: Vue 3, TypeScript, Pinia, Vue Router, Vite
- **通信**: REST API + WebSocket
