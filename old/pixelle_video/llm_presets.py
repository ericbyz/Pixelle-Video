# Copyright (C) 2025 AIDC-AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
LLM Presets - Predefined configurations for popular LLM providers

All providers support OpenAI SDK protocol.
"""

from typing import Dict, Any, List


LLM_PRESETS: List[Dict[str, Any]] = [
    {
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-v4-pro",
        "api_key_url": "https://platform.deepseek.com/api_keys",
        "models": [
            {"id": "deepseek-v4-pro", "name": "DeepSeek-V4-Pro (旗舰)"},
            {"id": "deepseek-v4-flash", "name": "DeepSeek-V4-Flash (极速)"},
        ],
    },
    {
        "name": "Qwen (通义千问)",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-max",
        "api_key_url": "https://bailian.console.aliyun.com/?tab=model#/api-key",
        "models": [
            {"id": "qwen-max", "name": "Qwen-Max (最强)"},
            {"id": "qwen-plus", "name": "Qwen-Plus (高性价比)"},
            {"id": "qwen-turbo", "name": "Qwen-Turbo (最快)"},
            {"id": "qwen3-235b-a22b", "name": "Qwen3-235B-A22B (旗舰MoE)"},
            {"id": "qwen3-30b-a3b", "name": "Qwen3-30B-A3B (高效MoE)"},
            {"id": "qwen3-32b", "name": "Qwen3-32B (稠密)"},
            {"id": "qwen3-4b", "name": "Qwen3-4B (轻量)"},
            {"id": "qwen-long", "name": "Qwen-Long (超长上下文)"},
        ],
    },
    {
        "name": "GLM (智谱)",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-5",
        "api_key_url": "https://open.bigmodel.cn/usercenter/apikeys",
        "models": [
            {"id": "glm-5", "name": "GLM-5 (最新旗舰)"},
            {"id": "glm-5-turbo", "name": "GLM-5-Turbo (高速)"},
            {"id": "glm-4", "name": "GLM-4"},
            {"id": "glm-4-flash-250414", "name": "GLM-4-Flash (免费)"},
            {"id": "glm-0", "name": "GLM-0"},
            {"id": "glm-new", "name": "GLM-New"},
        ],
    },
    {
        "name": "Doubao (豆包)",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "model": "doubao-1.5-pro-32k",
        "api_key_url": "https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey",
        "models": [
            {"id": "doubao-1.5-pro-32k", "name": "Doubao-1.5-Pro 32K"},
            {"id": "doubao-1.5-pro-256k", "name": "Doubao-1.5-Pro 256K"},
            {"id": "doubao-1.5-lite-32k", "name": "Doubao-1.5-Lite 32K"},
            {"id": "doubao-pro-32k", "name": "Doubao-Pro 32K"},
            {"id": "doubao-pro-128k", "name": "Doubao-Pro 128K"},
            {"id": "doubao-lite-32k", "name": "Doubao-Lite 32K"},
        ],
    },
    {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o",
        "api_key_url": "https://platform.openai.com/api-keys",
        "models": [
            {"id": "gpt-5.4", "name": "GPT-5.4 (最新)"},
            {"id": "gpt-5.4-mini", "name": "GPT-5.4 Mini"},
            {"id": "gpt-4.1", "name": "GPT-4.1"},
            {"id": "gpt-4.1-mini", "name": "GPT-4.1 Mini"},
            {"id": "gpt-4o", "name": "GPT-4o"},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
            {"id": "o3", "name": "o3 (推理)"},
            {"id": "o4-mini", "name": "o4-mini (推理)"},
        ],
    },
    {
        "name": "Claude",
        "base_url": "https://api.anthropic.com/v1/",
        "model": "claude-sonnet-4-6",
        "api_key_url": "https://console.anthropic.com/settings/keys",
        "models": [
            {"id": "claude-opus-4-8", "name": "Claude Opus 4.8 (最强)"},
            {"id": "claude-opus-4-7", "name": "Claude Opus 4.7"},
            {"id": "claude-sonnet-4-6", "name": "Claude Sonnet 4.6 (推荐)"},
            {"id": "claude-haiku-4-5", "name": "Claude Haiku 4.5 (快速)"},
        ],
    },
    {
        "name": "Moonshot (月之暗面)",
        "base_url": "https://api.moonshot.cn/v1",
        "model": "moonshot-v1-8k",
        "api_key_url": "https://platform.moonshot.cn/console/api-keys",
        "models": [
            {"id": "moonshot-v1-8k", "name": "Moonshot-v1 8K"},
            {"id": "moonshot-v1-32k", "name": "Moonshot-v1 32K"},
            {"id": "moonshot-v1-128k", "name": "Moonshot-v1 128K"},
        ],
    },
    {
        "name": "Minimax",
        "base_url": "https://api.minimax.chat/v1",
        "model": "MiniMax-Text-01",
        "api_key_url": "https://platform.minimax.io/user-center/basic-information/interface-key",
        "models": [
            {"id": "MiniMax-Text-01", "name": "MiniMax-Text-01"},
            {"id": "abab6.5s-chat", "name": "Abab6.5s"},
        ],
    },
    {
        "name": "Ollama (本地)",
        "base_url": "http://localhost:11434/v1",
        "model": "llama3.2",
        "api_key_url": "https://ollama.com/download",
        "default_api_key": "ollama",
        "models": [],
    },
]


def get_preset_names() -> List[str]:
    """Get list of preset names"""
    return [preset["name"] for preset in LLM_PRESETS]


def get_preset(name: str) -> Dict[str, Any]:
    """Get preset configuration by name"""
    for preset in LLM_PRESETS:
        if preset["name"] == name:
            return preset
    return {}


def find_preset_by_base_url_and_model(base_url: str, model: str) -> str | None:
    """
    Find preset name by base_url and model

    Returns:
        Preset name if found, None otherwise
    """
    for preset in LLM_PRESETS:
        if preset["base_url"] == base_url and preset["model"] == model:
            return preset["name"]
    return None
