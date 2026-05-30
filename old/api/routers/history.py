from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from api.dependencies import PixelleVideoDep
from api.schemas.history import (
    DeleteResponse,
    DuplicateResponse,
    StatisticsResponse,
    TaskDetailResponse,
    TaskListResponse,
)

router = APIRouter(prefix="/history", tags=["History"])


@router.get("/tasks", response_model=TaskListResponse)
async def get_task_list(
    pixelle_video: PixelleVideoDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    status: Optional[str] = None,
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
):
    result = await pixelle_video.history.get_task_list(
        page=page,
        page_size=page_size,
        status=status,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return TaskListResponse(**result)


@router.get("/tasks/{task_id}", response_model=TaskDetailResponse)
async def get_task_detail(task_id: str, pixelle_video: PixelleVideoDep):
    result = await pixelle_video.history.get_task_detail(task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskDetailResponse(**result)


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(pixelle_video: PixelleVideoDep):
    result = await pixelle_video.history.get_statistics()
    return StatisticsResponse(success=True, **result)


@router.delete("/tasks/{task_id}", response_model=DeleteResponse)
async def delete_task(task_id: str, pixelle_video: PixelleVideoDep):
    deleted = await pixelle_video.history.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return DeleteResponse()


@router.post("/tasks/{task_id}/duplicate", response_model=DuplicateResponse)
async def duplicate_task(task_id: str, pixelle_video: PixelleVideoDep):
    result = await pixelle_video.history.duplicate_task(task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return DuplicateResponse(data=result)
