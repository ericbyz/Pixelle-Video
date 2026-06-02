from fastapi import APIRouter, HTTPException
from loguru import logger

from api.dependencies import PixelleVideoDep
from schemas.config import (
    ConfigUpdateRequest,
    ConfigResponse,
    TestLLMRequest,
    TestLLMResponse,
    TestComfyUIRequest,
    TestComfyUIResponse,
    LLMPresetResponse,
    LLMModelsResponse,
    VersionResponse,
    ImagePresetResponse,
    VideoPresetResponse,
)

router = APIRouter(prefix="/config", tags=["Config"])

_MASKED = "********"


def _mask_config(config_dict: dict) -> dict:
    """Mask sensitive fields in config for frontend display."""
    result = {}
    for key, value in config_dict.items():
        if isinstance(value, dict):
            result[key] = _mask_config(value)
        elif _is_sensitive_key(key) and isinstance(value, str) and value:
            result[key] = _MASKED
        else:
            result[key] = value
    return result


def _is_sensitive_key(key: str) -> bool:
    return "api_key" in key or "password" in key or "secret" in key


def _merge_updates(config_dict: dict, updates: dict) -> dict:
    """Merge updates, keeping masked values unchanged."""
    result = dict(config_dict)
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge_updates(result[key], value)
        elif value == _MASKED:
            continue
        else:
            result[key] = value
    return result


@router.get("", response_model=ConfigResponse)
async def get_config():
    from pixelle_video.config import config_manager

    config_dict = config_manager.config.to_dict()
    masked = _mask_config(config_dict)
    return ConfigResponse(config=masked)


@router.put("", response_model=ConfigResponse)
async def update_config(
    request: ConfigUpdateRequest,
):
    from pixelle_video.config import config_manager

    updates = request.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided")

    current = config_manager.config.to_dict()
    merged = _merge_updates(current, updates)

    try:
        config_manager.config = config_manager.config.__class__(**merged)
        config_manager.save()
    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    config_dict = config_manager.config.to_dict()
    masked = _mask_config(config_dict)
    return ConfigResponse(config=masked)


@router.post("/test-llm", response_model=TestLLMResponse)
async def test_llm_connection(
    request: TestLLMRequest,
):
    from pixelle_video.config import config_manager

    api_key = request.api_key
    base_url = request.base_url
    model = request.model

    if api_key == _MASKED or not api_key:
        api_key = config_manager.config.llm.api_key
    if base_url == _MASKED or not base_url:
        base_url = config_manager.config.llm.base_url
    if model == _MASKED or not model:
        model = config_manager.config.llm.model

    if not all([api_key, base_url, model]):
        return TestLLMResponse(success=False, message="LLM not fully configured")

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Hi, reply with OK"}],
            max_tokens=10,
        )
        content = response.choices[0].message.content
        return TestLLMResponse(success=True, message=f"LLM connected: {content}")
    except Exception as e:
        logger.error(f"LLM test failed: {e}")
        return TestLLMResponse(success=False, message=str(e))


@router.post("/test-comfyui", response_model=TestComfyUIResponse)
async def test_comfyui_connection(
    request: TestComfyUIRequest,
):
    import json
    import urllib.request
    import urllib.error
    from pixelle_video.config import config_manager

    comfyui_url = request.comfyui_url
    api_key = request.comfyui_api_key

    if not comfyui_url or comfyui_url == _MASKED:
        comfyui_url = config_manager.config.comfyui.comfyui_url
    if not api_key or api_key == _MASKED:
        api_key = config_manager.config.comfyui.comfyui_api_key

    if not comfyui_url:
        return TestComfyUIResponse(success=False, message="ComfyUI URL not configured")

    url = f"{comfyui_url.rstrip('/')}/system_stats"
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        devices = data.get("devices", [])
        gpu_info = ""
        if devices:
            gpu_names = [d.get("name", "Unknown") for d in devices]
            gpu_info = f" | GPU: {', '.join(gpu_names)}"
        return TestComfyUIResponse(
            success=True,
            message=f"Connected{gpu_info}",
            system_info=data,
        )
    except urllib.error.HTTPError as e:
        return TestComfyUIResponse(
            success=False, message=f"Connection failed: HTTP {e.code}"
        )
    except urllib.error.URLError:
        return TestComfyUIResponse(success=False, message="Cannot connect to ComfyUI server")
    except TimeoutError:
        return TestComfyUIResponse(success=False, message="Connection timed out (10s)")
    except Exception as e:
        logger.error(f"ComfyUI test failed: {e}")
        return TestComfyUIResponse(success=False, message=str(e))


@router.get("/llm-presets", response_model=LLMPresetResponse)
async def get_llm_presets():
    from pixelle_video.llm_presets import LLM_PRESETS

    return LLMPresetResponse(presets=LLM_PRESETS)


@router.get("/llm-models", response_model=LLMModelsResponse)
async def get_llm_models(
    api_key: str = None,
    base_url: str = None,
):
    from pixelle_video.config import config_manager

    if not api_key or api_key == _MASKED:
        api_key = config_manager.config.llm.api_key
    if not base_url or base_url == _MASKED:
        base_url = config_manager.config.llm.base_url

    if not api_key or not base_url:
        return LLMModelsResponse(models=[])

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key, base_url=base_url)
        models_resp = client.models.list()
        models = [
            {"id": m.id, "name": m.id}
            for m in models_resp.data
        ]
        return LLMModelsResponse(models=models)
    except Exception as e:
        logger.error(f"Failed to fetch models: {e}")
        return LLMModelsResponse(models=[])


@router.get("/version", response_model=VersionResponse)
async def get_version():
    return VersionResponse()


@router.get("/image-presets", response_model=ImagePresetResponse)
async def get_image_presets():
    from pixelle_video.image_presets import IMAGE_PRESETS

    return ImagePresetResponse(presets=IMAGE_PRESETS)


@router.get("/video-presets", response_model=VideoPresetResponse)
async def get_video_presets():
    from pixelle_video.video_presets import VIDEO_PRESETS

    return VideoPresetResponse(presets=VIDEO_PRESETS)
