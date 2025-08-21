import os
import json
import base64
import websockets
import uuid
import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

MURF_API_KEY = os.environ.get("MURF_API_KEY", "")
MURF_WS_URL = (
    f"wss://api.murf.ai/v1/speech/stream-input"
    f"?api-key={MURF_API_KEY}&sample_rate=44100&channel_type=MONO&format=MP3"
)


async def stream_gemini_to_murf(text: str, output_path: str = None) -> str:
    """
    Streams text to Murf AI via WebSocket and saves synthesized audio as MP3.
    Returns the absolute path to the audio file.
    """
    if not MURF_API_KEY:
        raise RuntimeError("MURF_API_KEY not set in environment")

    audio_bytes = bytearray()

    # Prepare output path
    base_dir = Path(__file__).resolve().parent.parent.parent
    receiver_dir = base_dir / "receiver_audio"
    receiver_dir.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    if not output_path:
        output_path = receiver_dir / f"output_{timestamp}_{unique_id}.mp3"
    else:
        output_path = Path(output_path)

    print(f"[MURF] Saving output to {output_path}")

    try:
        async with websockets.connect(MURF_WS_URL) as ws:
            print("[MURF] ✅ Connected to Murf WebSocket")

            # 1. Send voice config
            voice_cfg = {
                "voice_config": {
                    "voiceId": "en-US-amara",
                    "style": "Conversational",
                    "rate": 0,
                    "pitch": 0,
                    "variation": 1,
                }
            }
            await ws.send(json.dumps(voice_cfg))
            print("[MURF] Sent voice_config")

            # 2. Send text
            await ws.send(json.dumps({"text": text}))
            print(f"[MURF] Sent text: {text}")

            # 3. Send end signal
            await ws.send(json.dumps({"end": True}))
            print("[MURF] Sent end signal")

            # 4. Collect audio chunks with max chunk count and timeout
            import asyncio
            max_chunks = 50
            chunk_count = 0
            timeout_seconds = 10
            start_time = datetime.datetime.now()
            while True:
                try:
                    raw_msg = await asyncio.wait_for(ws.recv(), timeout=timeout_seconds)
                except asyncio.TimeoutError:
                    print(f"[MURF] Timeout waiting for audio chunk after {timeout_seconds} seconds.")
                    break
                chunk_count += 1
                try:
                    msg = json.loads(raw_msg)
                except Exception:
                    print(f"[MURF] Non-JSON message: {raw_msg}")
                    continue

                if "audio" in msg:
                    chunk = base64.b64decode(msg["audio"])
                    audio_bytes.extend(chunk)
                    print(f"[MURF] 🔊 Received chunk ({len(chunk)} bytes)")
                if msg.get("final"):
                    print("[MURF] ✅ Synthesis complete")
                    break
                if chunk_count >= max_chunks:
                    print(f"[MURF] Max chunk count {max_chunks} reached, breaking loop.")
                    break

    except Exception as e:
        raise RuntimeError(f"[MURF] WebSocket error: {e}")

    # Save audio
    print(f"[MURF] Attempting to write {len(audio_bytes)} bytes to {output_path}")
    try:
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        print(f"[MURF] Saved audio ({len(audio_bytes)} bytes) → {output_path}")
    except Exception as e:
        print(f"[MURF] Failed to write audio file: {e}")
        raise RuntimeError(f"[MURF] Failed to write audio file: {e}")

    return str(output_path.resolve())
