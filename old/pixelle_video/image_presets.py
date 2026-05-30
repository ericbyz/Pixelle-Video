"""
Image Generation Service Presets - Predefined configurations for popular image generation providers
"""

from typing import Dict, Any, List

IMAGE_PRESETS: List[Dict[str, Any]] = [
    {
        "name": "Volcengine Visual (火山引擎智能视觉)",
        "provider": "volcengine",
        "base_url": "https://visual.volcengineapi.com",
        "models": [
            {"id": "high_aes_general_v20_L", "name": "通用2.0L (高质量)"},
            {"id": "high_aes_general_v21", "name": "通用2.1"},
            {"id": "high_aes_general_v23", "name": "通用2.3"},
            {"id": "high_aes_general_v30", "name": "通用3.0 (最新)"},
            {"id": "high_aes_general_v30_L", "name": "通用3.0L (极致质量)"},
        ],
        "api_key_url": "https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey",
        "description": "火山引擎智能视觉文生图，支持高质量中文描述生成图片",
    },
    {
        "name": "Doubao SeedDream (豆包)",
        "provider": "doubao",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "models": [
            {"id": "doubao-seedream-5-0-260128", "name": "SeedDream 5.0 (最新)"},
            {"id": "doubao-seedream-4-0-t2i-250415", "name": "SeedDream 4.0"},
            {"id": "doubao-seedream-3-0-t2i-250415", "name": "SeedDream 3.0"},
            {"id": "doubao-seedream-2-1-t2i-250315", "name": "SeedDream 2.1"},
        ],
        "api_key_url": "https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey",
        "description": "豆包SeedDream文生图，中文理解优秀，画质精细",
    },
    {
        "name": "Qwen Image (通义万相)",
        "provider": "qwen",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "models": [
            {"id": "wanx2.1-t2i-turbo", "name": "万相2.1 极速"},
            {"id": "wanx2.1-t2i-plus", "name": "万相2.1 Plus (高质量)"},
            {"id": "wanx-v1", "name": "通义万相 v1"},
        ],
        "api_key_url": "https://bailian.console.aliyun.com/?tab=model#/api-key",
        "description": "阿里通义万相文生图，中文理解出色",
    },
    {
        "name": "Zhipu CogView (智谱)",
        "provider": "zhipu",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "models": [
            {"id": "cogview-4-250304", "name": "CogView-4 (最新)"},
            {"id": "cogview-4", "name": "CogView-4"},
        ],
        "api_key_url": "https://open.bigmodel.cn/usercenter/apikeys",
        "description": "智谱CogView文生图模型",
    },
]


def get_image_preset_names() -> List[str]:
    return [p["name"] for p in IMAGE_PRESETS]


def get_image_preset(name: str) -> Dict[str, Any]:
    for p in IMAGE_PRESETS:
        if p["name"] == name:
            return p
    return {}
