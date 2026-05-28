from typing import Optional, List, Any
from pydantic import BaseModel, Field


class LLMConfigUpdate(BaseModel):
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None


class ComfyUIConfigUpdate(BaseModel):
    comfyui_url: Optional[str] = None
    comfyui_api_key: Optional[str] = None
    runninghub_api_key: Optional[str] = None
    runninghub_concurrent_limit: Optional[int] = Field(None, ge=1, le=10)
    runninghub_instance_type: Optional[str] = None


class TTSConfigUpdate(BaseModel):
    inference_mode: Optional[str] = None
    default_workflow: Optional[str] = None


class ImageConfigUpdate(BaseModel):
    default_workflow: Optional[str] = None
    prompt_prefix: Optional[str] = None


class VideoConfigUpdate(BaseModel):
    default_workflow: Optional[str] = None
    prompt_prefix: Optional[str] = None


class ConfigUpdateRequest(BaseModel):
    llm: Optional[LLMConfigUpdate] = None
    comfyui: Optional[ComfyUIConfigUpdate] = None
    tts: Optional[TTSConfigUpdate] = None
    image: Optional[ImageConfigUpdate] = None
    video: Optional[VideoConfigUpdate] = None
    default_template: Optional[str] = None


class ConfigResponse(BaseModel):
    success: bool = True
    config: Optional[Any] = None


class TestLLMRequest(BaseModel):
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None


class TestLLMResponse(BaseModel):
    success: bool = True
    message: str = ""


class LLMPresetResponse(BaseModel):
    success: bool = True
    presets: List[Any] = []


class LLMModelInfo(BaseModel):
    id: str
    name: Optional[str] = None


class LLMModelsResponse(BaseModel):
    success: bool = True
    models: List[LLMModelInfo] = []


class VersionResponse(BaseModel):
    success: bool = True
    version: str = "0.1.0"
    service: str = "Pixelle-Video API"
