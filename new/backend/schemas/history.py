from typing import Optional, List, Any
from pydantic import BaseModel, Field


class TaskListQuery(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    status: Optional[str] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"


class TaskMetadataBrief(BaseModel):
    task_id: str
    title: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration: Optional[float] = None
    file_size: Optional[int] = None


class TaskListResponse(BaseModel):
    success: bool = True
    tasks: List[Any] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0


class TaskDetailResponse(BaseModel):
    success: bool = True
    metadata: Optional[Any] = None
    storyboard: Optional[Any] = None


class StatisticsResponse(BaseModel):
    success: bool = True
    total_tasks: int = 0
    completed: int = 0
    failed: int = 0
    total_duration: float = 0.0
    total_size: int = 0


class DuplicateResponse(BaseModel):
    success: bool = True
    message: str = "Success"
    data: Optional[Any] = None


class DeleteResponse(BaseModel):
    success: bool = True
    message: str = "Task deleted"
