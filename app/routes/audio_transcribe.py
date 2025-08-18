import os
import logging
import tempfile
import wave
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
import assemblyai as aai

logging.basicConfig(level=logging.INFO)
router = APIRouter()

load_dotenv()
API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
aai.settings.api_key = API_KEY

@router.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    await websocket.accept()
    logging.info("Client connected for transcription")

    pcm_buffer = bytearray()
    try:
        while True:
            chunk = await websocket.receive_bytes()
            pcm_buffer.extend(chunk)
    except WebSocketDisconnect:
        logging.info("Client disconnected, starting transcription")

    # Save PCM buffer to valid WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as audio_file:
        temp_audio_path = audio_file.name
        with wave.open(audio_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit PCM
            wf.setframerate(16000)
            wf.writeframes(pcm_buffer)

    try:
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(temp_audio_path)
        if transcript.status == aai.TranscriptStatus.error:
            logging.error(f"Transcription failed: {transcript.error}")
        else:
            logging.info(f"\nFull Transcript:\n{transcript.text}")
    except Exception as e:
        logging.error(f"Error during transcription: {e}")
    finally:
        os.remove(temp_audio_path)
        
