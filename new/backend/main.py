"""
Pixelle-Video Separated Backend - FastAPI Application

Run:
    python main.py
    python main.py --host 0.0.0.0 --port 8000 --reload
"""

import sys
from pathlib import Path

_backend_dir = Path(__file__).resolve().parent.parent  # new/
_project_root = _backend_dir.parent / "old"  # old/
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

# Change working directory to old/ so config_manager finds config.yaml
import os
os.chdir(str(_project_root))

import argparse
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from api.config import api_config
from api.tasks import task_manager
from api.dependencies import shutdown_pixelle_video

from api.routers import (
    health_router,
    llm_router,
    tts_router,
    image_router,
    content_router,
    video_router,
    tasks_router,
    files_router,
    resources_router,
    frame_router,
)

from routers import (
    history_router,
    config_router,
    ws_router,
    upload_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Pixelle-Video Backend...")
    await task_manager.start()
    logger.info("Pixelle-Video Backend started")

    yield

    logger.info("Shutting down Pixelle-Video Backend...")
    await task_manager.stop()
    await shutdown_pixelle_video()
    logger.info("Pixelle-Video Backend shutdown complete")


app = FastAPI(
    title="Pixelle-Video API",
    description="Pixelle-Video - AI Video Generation Platform API",
    version="0.1.0",
    docs_url=api_config.docs_url,
    redoc_url=api_config.redoc_url,
    openapi_url=api_config.openapi_url,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Existing routers from api/
app.include_router(health_router)
app.include_router(llm_router, prefix=api_config.api_prefix)
app.include_router(tts_router, prefix=api_config.api_prefix)
app.include_router(image_router, prefix=api_config.api_prefix)
app.include_router(content_router, prefix=api_config.api_prefix)
app.include_router(video_router, prefix=api_config.api_prefix)
app.include_router(tasks_router, prefix=api_config.api_prefix)
app.include_router(files_router, prefix=api_config.api_prefix)
app.include_router(resources_router, prefix=api_config.api_prefix)
app.include_router(frame_router, prefix=api_config.api_prefix)

# New routers for separated backend
app.include_router(history_router, prefix=api_config.api_prefix)
app.include_router(config_router, prefix=api_config.api_prefix)
app.include_router(ws_router)
app.include_router(upload_router, prefix=api_config.api_prefix)


@app.get("/")
async def root():
    return {
        "service": "Pixelle-Video API",
        "version": "0.1.0",
        "docs": api_config.docs_url,
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser(description="Start Pixelle-Video Backend Server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )
