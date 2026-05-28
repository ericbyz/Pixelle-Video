from .history import router as history_router
from .config import router as config_router
from .websocket import router as ws_router
from .upload import router as upload_router

__all__ = [
    "history_router",
    "config_router",
    "ws_router",
    "upload_router",
]
