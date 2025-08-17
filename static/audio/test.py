import asyncio
import websockets

async def test_audio_ws():
    uri = "ws://127.0.0.1:8000/ws/audio?session=test123"
    async with websockets.connect(uri) as websocket:
        with open("havard.wav", "rb") as f:
            while chunk := f.read(1024):  # send in chunks
                await websocket.send(chunk)
        print("✅ Audio sent")

asyncio.run(test_audio_ws())
