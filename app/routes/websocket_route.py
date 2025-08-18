from fastapi import APIRouter, WebSocket
import logging

logging.basicConfig(level=logging.INFO)
router = APIRouter()

@router.websocket("/ws/audio")
async def audio_handler(websocket: WebSocket):
    await websocket.accept()
    logging.info("Client connected to audio WebSocket")

    audio_file_path = "received_audio.raw"  # You can use .wav if header is handled on client
    try:
        with open(audio_file_path, "wb") as audio_file:
            while True:
                data = await websocket.receive_bytes()
                audio_file.write(data)
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()
