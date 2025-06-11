"""
WebSocket роутер для real-time коммуникации
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging

logger = logging.getLogger(__name__)

websocket_router = APIRouter()

# Менеджер активных соединений
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket подключен. Всего соединений: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket отключен. Всего соединений: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Ошибка отправки сообщения: {e}")

manager = ConnectionManager()

@websocket_router.websocket("/connect")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # TODO: Обработка сообщений
            await websocket.send_json({"echo": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket) 