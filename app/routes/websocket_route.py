from fastapi import APIRouter, WebSocket
import logging
import base64

logging.basicConfig(level=logging.INFO)
router = APIRouter()

@router.websocket("/ws/audio")
async def audio_handler(websocket: WebSocket):
    await websocket.accept()
    logging.info("Client connected to audio WebSocket")

    audio_chunks = []  # Array to accumulate base64 chunks
    try:
        while True:
            data = await websocket.receive_bytes()
            base64_chunk = base64.b64encode(data).decode('utf-8')  # Convert to base64
            audio_chunks.append(base64_chunk)  # Accumulate the chunk
            logging.info("Received audio chunk, base64 data length: %d", len(base64_chunk))
            print("Acknowledgement: Audio data received.")
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()
