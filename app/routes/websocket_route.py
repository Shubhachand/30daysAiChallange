import logging
from fastapi import APIRouter, WebSocket

log = logging.getLogger("app.websocket")

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            log.info(f"Received from client: {data}")
            await websocket.send_text(f"Echo: {data}")
    except Exception as e:
        log.info(f"WebSocket disconnected: {e}")
