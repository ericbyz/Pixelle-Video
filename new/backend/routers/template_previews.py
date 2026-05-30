from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/template-previews", tags=["Template Previews"])

_IMAGE_MEDIA_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


def _old_docs_images_dir() -> Path:
    repo_root = Path(__file__).resolve().parents[3]
    return repo_root / "old" / "docs" / "images"


def _extract_size_and_stem(template_path: str) -> tuple[str, str]:
    parts = Path(template_path).parts
    if any(part in {"", ".", ".."} for part in parts):
        raise HTTPException(status_code=400, detail="Invalid template path")

    template_file = Path(parts[-1])
    if template_file.suffix != ".html":
        raise HTTPException(status_code=400, detail="Template path must end with .html")

    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="Template path must include size")

    size = parts[-2]
    if "x" not in size:
        raise HTTPException(status_code=400, detail="Template size is invalid")

    return size, template_file.stem


@router.get("/{template_path:path}")
async def get_template_preview(template_path: str):
    size, stem = _extract_size_and_stem(template_path)
    base_dir = _old_docs_images_dir()

    for suffix, media_type in _IMAGE_MEDIA_TYPES.items():
        preview_path = base_dir / size / f"{stem}{suffix}"
        if preview_path.exists() and preview_path.is_file():
            return FileResponse(
                path=str(preview_path),
                media_type=media_type,
                headers={"Cache-Control": "public, max-age=3600"},
            )

    raise HTTPException(status_code=404, detail="Template preview not found")
