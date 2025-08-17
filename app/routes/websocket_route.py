import os
import logging
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()
logger = logging.getLogger("app.websocket")

UPLOAD_DIR = "static/audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("🎙️ WebSocket connection established for audio streaming.")

    session_id = websocket.query_params.get("session", "none")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    file_path = os.path.join(
        UPLOAD_DIR, f"streamed_audio_session_{session_id}_{timestamp}.webm"
    )
    logger.info(f"📂 Saving streamed audio to: {file_path}")

    try:
        with open(file_path, "wb") as f:
            while True:
                try:
                    chunk = await websocket.receive_bytes()
                    f.write(chunk)
                    f.flush()
                    logger.debug(f"Received audio chunk of size: {len(chunk)} bytes")
                except WebSocketDisconnect:
                    logger.info("⚡ WebSocket disconnected by client.")
                    break
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket connection closed.")
    except Exception as e:
        logger.error(f"❌ Error in WebSocket: {e}")
    finally:
        logger.info(f"✅ Audio stream saved at {file_path}")
