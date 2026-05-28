import asyncio
import json
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

router = APIRouter(tags=["WebSocket"])


class ConnectionManager:
    def __init__(self):
        self._connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, task_id: str, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            if task_id not in self._connections:
                self._connections[task_id] = set()
            self._connections[task_id].add(websocket)
        logger.debug(f"WebSocket connected for task {task_id}")

    async def disconnect(self, task_id: str, websocket: WebSocket):
        async with self._lock:
            if task_id in self._connections:
                self._connections[task_id].discard(websocket)
                if not self._connections[task_id]:
                    del self._connections[task_id]
        logger.debug(f"WebSocket disconnected for task {task_id}")

    async def broadcast(self, task_id: str, data: dict):
        async with self._lock:
            connections = list(self._connections.get(task_id, set()))

        payload = json.dumps(data, ensure_ascii=False)
        for ws in connections:
            try:
                await ws.send_text(payload)
            except Exception:
                pass

    async def send_progress(
        self,
        task_id: str,
        current: int,
        total: int,
        message: str = "",
        status: str = "running",
    ):
        await self.broadcast(task_id, {
            "type": "progress",
            "task_id": task_id,
            "current": current,
            "total": total,
            "percentage": round(current / total * 100, 1) if total > 0 else 0,
            "message": message,
            "status": status,
        })

    async def send_complete(self, task_id: str, result: dict = None):
        await self.broadcast(task_id, {
            "type": "complete",
            "task_id": task_id,
            "status": "completed",
            "result": result,
        })

    async def send_error(self, task_id: str, error: str):
        await self.broadcast(task_id, {
            "type": "error",
            "task_id": task_id,
            "status": "failed",
            "error": error,
        })


ws_manager = ConnectionManager()


@router.websocket("/ws/progress/{task_id}")
async def ws_progress(websocket: WebSocket, task_id: str):
    await ws_manager.connect(task_id, websocket)
    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                await websocket.send_text(json.dumps({"type": "heartbeat"}))
    except WebSocketDisconnect:
        await ws_manager.disconnect(task_id, websocket)
    except Exception:
        await ws_manager.disconnect(task_id, websocket)
