"""
Video Generation Service Presets - Predefined configurations for popular video generation providers
"""

from typing import Dict, Any, List

VIDEO_PRESETS: List[Dict[str, Any]] = [
    {
        "name": "Doubao SeedDance (豆包)",
        "provider": "doubao",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "models": [
            {"id": "doubao-seedance-1-0-pro-fast-251015", "name": "SeedDance 1.0 Pro Fast (默认)"},
            {"id": "doubao-seedance-1-0-lite-i2v-250428", "name": "SeedDance 1.0 Lite 图生视频"},
            {"id": "doubao-seedance-1-0-lite-t2v-250428", "name": "SeedDance 1.0 Lite 文生视频"},
            {"id": "doubao-seedance-1-0-pro-250528", "name": "SeedDance 1.0 Pro"},
            {"id": "doubao-seedance-1-5-pro-251215", "name": "SeedDance 1.5 Pro"},
            {"id": "doubao-seedance-2-0-260128", "name": "SeedDance 2.0"},
            {"id": "doubao-seedance-2-0-fast-260128", "name": "SeedDance 2.0 Fast"},
        ],
        "api_key_url": "https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey",
        "description": "豆包SeedDance视频生成，支持文生视频和图生视频",
    },
    {
        "name": "Volcengine Jimeng (火山引擎即梦)",
        "provider": "volcengine",
        "base_url": "https://visual.volcengineapi.com",
        "models": [
            {"id": "jimeng_v21_t2v", "name": "即梦2.1 文生视频"},
            {"id": "jimeng_v21_i2v", "name": "即梦2.1 图生视频"},
            {"id": "jimeng_v20_t2v", "name": "即梦2.0 文生视频"},
            {"id": "jimeng_v20_i2v", "name": "即梦2.0 图生视频"},
        ],
        "api_key_url": "https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey",
        "description": "火山引擎即梦视频生成，支持文生视频和图生视频",
    },
    {
        "name": "Kling (可灵)",
        "provider": "kling",
        "base_url": "https://api.klingai.com",
        "models": [
            {"id": "kling-v1-6", "name": "可灵 v1.6 (最新)"},
            {"id": "kling-v1-5", "name": "可灵 v1.5"},
            {"id": "kling-v1", "name": "可灵 v1"},
        ],
        "api_key_url": "https://klingai.kuaishou.com/developer/user-center/api-secret-key",
        "description": "快手可灵视频生成，支持文生视频和图生视频",
    },
    {
        "name": "Zhipu CogVideoX (智谱)",
        "provider": "zhipu",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "models": [
            {"id": "cogvideox-5", "name": "CogVideoX-5 (高质量)"},
            {"id": "cogvideox-2", "name": "CogVideoX-2 (快速)"},
        ],
        "api_key_url": "https://open.bigmodel.cn/usercenter/apikeys",
        "description": "智谱CogVideoX视频生成模型",
    },
]


def get_video_preset_names() -> List[str]:
    return [p["name"] for p in VIDEO_PRESETS]


def get_video_preset(name: str) -> Dict[str, Any]:
    for p in VIDEO_PRESETS:
        if p["name"] == name:
            return p
    return {}
