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

from pixelle_video.models.media import MediaResult


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
            return await self._doubao_generate_video(prompt, duration, width, height)

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
        timeout = httpx.Timeout(connect=10.0, read=120, write=30, pool=30)
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        image_url = data["data"][0]["url"]
        logger.info(f"Image generated: {image_url}")
        return MediaResult(media_type="image", url=image_url)

    async def _doubao_generate_video(
        self, prompt: str, duration: float, width: int, height: int
    ) -> MediaResult:
        """Generate video via Ark API (SeedDance) - async task + polling"""
        api_key = self.video_service_config.get("api_key", "")
        base_url = self.video_service_config.get("base_url", "").rstrip("/")
        model = self.video_service_config.get("model", "")

        if not api_key or not base_url or not model:
            raise ValueError(
                "video_service api_key, base_url, model are all required for doubao provider"
            )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # Determine ratio from width/height
        ratio = self._width_height_to_ratio(width, height)

        # Create async task
        create_url = f"{base_url}/contents/generations/tasks"
        payload = {
            "model": model,
            "content": [{"type": "text", "text": prompt}],
            "ratio": ratio,
        }

        logger.info(f"Calling Ark Video API: {create_url} model={model} ratio={ratio}")
        timeout = httpx.Timeout(connect=10.0, read=30, write=30, pool=30)
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(create_url, json=payload, headers=headers)
            resp.raise_for_status()
            task_data = resp.json()

        task_id = task_data.get("id")
        if not task_id:
            raise ValueError(f"No task_id in response: {task_data}")

        logger.info(f"Video task created: {task_id}, polling for result...")

        # Poll for completion
        poll_url = f"{base_url}/contents/generations/tasks/{task_id}"
        poll_timeout = httpx.Timeout(connect=10.0, read=30, write=30, pool=30)
        max_polls = 120  # max 120 * 5s = 10 minutes
        for i in range(max_polls):
            await asyncio.sleep(5)
            async with httpx.AsyncClient(timeout=poll_timeout) as client:
                resp = await client.get(poll_url, headers=headers)
                resp.raise_for_status()
                status_data = resp.json()

            status = status_data.get("status", "")
            logger.debug(f"Video task {task_id} status: {status}")

            if status == "succeeded":
                video_url = status_data.get("content", {}).get("video_url", "")
                if not video_url:
                    raise ValueError(f"Task succeeded but no video_url: {status_data}")
                logger.info(f"Video generated: {video_url}")
                return MediaResult(
                    media_type="video",
                    url=video_url,
                    duration=duration,
                )

            if status in ("failed", "cancelled", "error"):
                error_msg = status_data.get("error", {}).get("message", str(status_data))
                raise ValueError(f"Video generation failed: {error_msg}")

        raise TimeoutError(f"Video task {task_id} did not complete in time")

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
