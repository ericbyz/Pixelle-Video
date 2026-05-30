"""
File upload endpoint
"""

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from loguru import logger

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = Path.cwd() / "output" / "uploads"


@router.post("")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file (image, video, audio)

    Returns the file path that can be used with /api/files/ endpoint.
    """
    from api.config import api_config

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Check file size
    contents = await file.read()
    if len(contents) > api_config.max_upload_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {api_config.max_upload_size // (1024*1024)}MB",
        )

    # Generate unique filename
    ext = Path(file.filename).suffix
    unique_name = f"{uuid.uuid4().hex[:12]}{ext}"

    # Save to uploads directory
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    save_path = UPLOAD_DIR / unique_name

    with open(save_path, "wb") as f:
        f.write(contents)

    relative_path = f"output/uploads/{unique_name}"
    logger.info(f"File uploaded: {file.filename} → {relative_path}")

    return {
        "success": True,
        "message": "File uploaded successfully",
        "data": {
            "path": relative_path,
            "filename": file.filename,
            "size": len(contents),
        },
    }
