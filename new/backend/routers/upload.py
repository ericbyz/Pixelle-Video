import os
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from loguru import logger

router = APIRouter(prefix="/upload", tags=["Upload"])

ALLOWED_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
ALLOWED_VIDEO_EXT = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
ALLOWED_AUDIO_EXT = {".mp3", ".wav", ".ogg", ".aac", ".flac", ".m4a"}
ALLOWED_EXT = ALLOWED_IMAGE_EXT | ALLOWED_VIDEO_EXT | ALLOWED_AUDIO_EXT

MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB

UPLOAD_DIR = "uploads"


def _ensure_upload_dir(subdir: str = "") -> Path:
    base = Path(UPLOAD_DIR)
    if subdir:
        base = base / subdir
    base.mkdir(parents=True, exist_ok=True)
    return base


def _get_file_category(ext: str) -> str:
    ext = ext.lower()
    if ext in ALLOWED_IMAGE_EXT:
        return "images"
    elif ext in ALLOWED_VIDEO_EXT:
        return "videos"
    elif ext in ALLOWED_AUDIO_EXT:
        return "audios"
    return "others"


@router.post("")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed: {ext}. Allowed: {', '.join(sorted(ALLOWED_EXT))}",
        )

    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {MAX_UPLOAD_SIZE // (1024*1024)}MB",
        )

    category = _get_file_category(ext)
    unique_name = f"{uuid.uuid4().hex}{ext}"

    upload_dir = _ensure_upload_dir(category)
    file_path = upload_dir / unique_name

    with open(file_path, "wb") as f:
        f.write(content)

    relative_path = str(file_path)
    file_size = len(content)

    logger.info(f"Uploaded file: {relative_path} ({file_size} bytes)")

    return {
        "success": True,
        "message": "File uploaded",
        "path": relative_path,
        "filename": file.filename,
        "size": file_size,
        "category": category,
    }
