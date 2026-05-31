"""API Usage Statistics Router."""

from fastapi import APIRouter, Query
from typing import Optional

from services.usage_tracker import usage_tracker

router = APIRouter(prefix="/usage", tags=["Usage"])


@router.get("/summary")
async def get_usage_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
):
    """Get usage summary with breakdowns by service, model, and date."""
    summary = usage_tracker.get_summary(days=days)
    return {"success": True, "data": summary}


@router.get("/records")
async def get_usage_records(
    service: Optional[str] = Query(None, description="Filter by service (llm, image, video, tts)"),
    model: Optional[str] = Query(None, description="Filter by model name"),
    days: int = Query(30, ge=1, le=365),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    """Get paginated usage records with optional filters."""
    result = usage_tracker.get_records(
        service=service, model=model, days=days, page=page, page_size=page_size,
    )
    return {"success": True, **result}


@router.get("/models")
async def get_usage_models():
    """Get all models that have usage records, with pricing info."""
    models = usage_tracker.get_models()
    return {"success": True, "models": models}


@router.get("/pricing")
async def get_pricing():
    """Get the full model pricing table."""
    pricing = usage_tracker.get_pricing()
    return {"success": True, "pricing": pricing}
