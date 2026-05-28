from fastapi import APIRouter, HTTPException
from loguru import logger

from api.dependencies import PixelleVideoDep
from schemas.config import (
    ConfigUpdateRequest,
    ConfigResponse,
    TestLLMRequest,
    TestLLMResponse,
    LLMPresetResponse,
    LLMModelsResponse,
    VersionResponse,
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


@router.get("/llm-presets", response_model=LLMPresetResponse)
async def get_llm_presets():
    from pixelle_video.llm_presets import LLM_PRESETS

    return LLMPresetResponse(presets=LLM_PRESETS)


@router.get("/llm-models", response_model=LLMModelsResponse)
async def get_llm_models():
    from pixelle_video.config import config_manager

    api_key = config_manager.config.llm.api_key
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
