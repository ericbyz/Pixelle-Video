"""
Cloud Media Service - Direct API calls for image/video generation

Supports:
- doubao (Ark API): SeedDream image + SeedDance video
- volcengine: Not implemented (use doubao instead)
"""

import asyncio
from typing import Optional

import httpx
from loguru import logger
from volcenginesdkarkruntime import AsyncArk

from pixelle_video.models.media import MediaResult
from services.usage_tracker import tracked_call


class CloudMediaService:
    """Cloud API media generation service"""

    def __init__(self, config: dict):
        self.config = config
        self.image_service_config = config.get("image_service", {})
        self.video_service_config = config.get("video_service", {})

    async def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        **kwargs,
    ) -> MediaResult:
        """Generate image using cloud API"""
        provider = self.image_service_config.get("provider", "comfyui")

        if provider == "comfyui":
            raise ValueError("CloudMediaService does not handle comfyui provider")

        if provider == "volcengine":
            raise ValueError(
                "volcengine Visual API requires AK/SK signing, not supported yet. "
                "Please change image_service provider to 'doubao' in config.yaml"
            )

        if provider == "doubao":
            return await self._doubao_generate_image(prompt, width, height)

        raise ValueError(f"Unsupported image provider: {provider}")

    async def generate_video(
        self,
        prompt: str,
        duration: float = 5.0,
        width: int = 1280,
        height: int = 720,
        image_url: Optional[str] = None,
        **kwargs,
    ) -> MediaResult:
        """Generate video using cloud API"""
        provider = self.video_service_config.get("provider", "comfyui")

        if provider == "comfyui":
            raise ValueError("CloudMediaService does not handle comfyui provider")

        if provider == "volcengine":
            raise ValueError(
                "volcengine Visual API requires AK/SK signing, not supported yet. "
                "Please change video_service provider to 'doubao' in config.yaml"
            )

        if provider == "doubao":
            return await self._doubao_generate_video(prompt, duration, width, height, image_url=image_url)

        raise ValueError(f"Unsupported video provider: {provider}")

    async def _doubao_generate_image(
        self, prompt: str, width: int, height: int
    ) -> MediaResult:
        """Generate image via Ark API (SeedDream)"""
        api_key = self.image_service_config.get("api_key", "")
        base_url = self.image_service_config.get("base_url", "").rstrip("/")
        model = self.image_service_config.get("model", "")

        if not api_key or not base_url or not model:
            raise ValueError(
                "image_service api_key, base_url, model are all required for doubao provider"
            )

        url = f"{base_url}/images/generations"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # SeedDream 5.0 requires at least 3686400 pixels
        # Scale up if needed while maintaining aspect ratio
        min_pixels = 3686400
        current_pixels = width * height
        if current_pixels < min_pixels:
            import math
            scale = math.sqrt(min_pixels / current_pixels)
            width = int(width * scale)
            height = int(height * scale)
            logger.info(f"Scaled up image size to {width}x{height} to meet minimum pixel requirement")

        # Ark API size format: "WxH"
        size = f"{width}x{height}"
        payload = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "response_format": "url",
        }

        logger.info(f"Calling Ark Image API: {url} model={model} size={size}")
        async with tracked_call("image", model, "generate"):
            timeout = httpx.Timeout(connect=10.0, read=120, write=30, pool=30)
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()

            image_url = data["data"][0]["url"]
            logger.info(f"Image generated: {image_url}")
            return MediaResult(media_type="image", url=image_url)

    async def _doubao_generate_video(
        self, prompt: str, duration: float, width: int, height: int,
        image_url: Optional[str] = None,
    ) -> MediaResult:
        """Generate video via Ark SDK (SeedDance) - async task + polling"""
        api_key = self.video_service_config.get("api_key", "")
        base_url = self.video_service_config.get("base_url", "").rstrip("/")
        model = self.video_service_config.get("model", "")

        if not api_key or not base_url or not model:
            raise ValueError(
                "video_service api_key, base_url, model are all required for doubao provider"
            )

        # Determine ratio: adaptive for i2v, calculated for t2v
        ratio = "adaptive" if image_url else self._width_height_to_ratio(width, height)

        # Build content array
        content = []
        if image_url:
            content.append({"type": "image_url", "image_url": {"url": image_url}})
        if prompt:
            content.append({"type": "text", "text": prompt})

        logger.info(f"Calling Ark Video API via SDK: model={model} ratio={ratio} i2v={bool(image_url)}")

        client = AsyncArk(api_key=api_key, base_url=base_url)
        async with tracked_call("video", model, "generate"):
            try:
                task = await client.content_generation.tasks.create(
                    model=model,
                    content=content,
                    ratio=ratio,
                )
                task_id = task.id
                logger.info(f"Video task created: {task_id}, polling for result...")

                max_polls = 120  # max 120 * 5s = 10 minutes
                for i in range(max_polls):
                    await asyncio.sleep(5)
                    result = await client.content_generation.tasks.get(task_id=task_id)
                    logger.debug(f"Video task {task_id} status: {result.status}")

                    if result.status == "succeeded":
                        video_url = result.content.video_url if result.content else ""
                        if not video_url:
                            raise ValueError(f"Task succeeded but no video_url in response")
                        logger.info(f"Video generated: {video_url}")
                        return MediaResult(
                            media_type="video",
                            url=video_url,
                            duration=duration,
                        )

                    if result.status in ("failed", "cancelled", "error"):
                        error_msg = result.error.message if result.error else str(result.status)
                        raise ValueError(f"Video generation failed: {error_msg}")

                raise TimeoutError(f"Video task {task_id} did not complete in time")
            finally:
                await client.close()

    @staticmethod
    def _width_height_to_ratio(width: int, height: int) -> str:
        """Convert width/height to Ark API ratio string"""
        # Common ratios
        ratios = {
            (16, 9): "16:9",
            (9, 16): "9:16",
            (4, 3): "4:3",
            (3, 4): "3:4",
            (1, 1): "1:1",
        }
        # Find closest match
        from math import gcd
        g = gcd(width, height)
        simplified = (width // g, height // g)
        # Try direct match first
        if simplified in ratios:
            return ratios[simplified]
        # Try common ratios with tolerance
        aspect = width / height
        if abs(aspect - 16 / 9) < 0.1:
            return "16:9"
        if abs(aspect - 9 / 16) < 0.1:
            return "9:16"
        if abs(aspect - 4 / 3) < 0.1:
            return "4:3"
        if abs(aspect - 3 / 4) < 0.1:
            return "3:4"
        if abs(aspect - 1.0) < 0.1:
            return "1:1"
        # Default
        return "16:9"
