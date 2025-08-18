import os
import assemblyai as aai
from fastapi import FastAPI, WebSocket
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()

aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

@app.websocket("/ws/transcribe")
async def transcribe_audio(websocket: WebSocket):
    await websocket.accept()
    logging.info("Client connected to transcription WebSocket")

    transcriber = aai.RealtimeTranscriber(
        sample_rate=16000,
        on_data=lambda transcript: print("Transcript:", transcript.text),
        on_error=lambda err: print("Error:", err)
    )

    transcriber.connect()

    try:
        while True:
            data = await websocket.receive_bytes()
            transcriber.send_audio(data)
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
    finally:
        transcriber.close()
        await websocket.close()
