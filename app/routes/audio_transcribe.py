from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import os
import json
import websockets
import asyncio
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

router = APIRouter()

@router.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    await websocket.accept()
    print("Client connected to /ws/transcribe")

    url = "wss://streaming.assemblyai.com/v3/ws?sample_rate=16000"
    headers = {"Authorization": API_KEY}

    try:
        async with websockets.connect(url, extra_headers=headers) as assemblyai_ws:

            async def forward_audio():
                try:
                    while True:
                        # Receive binary audio chunk from client
                        audio_chunk = await websocket.receive_bytes()
                        print(f"Received audio chunk size: {len(audio_chunk)} bytes")
                        await assemblyai_ws.send(audio_chunk)
                except WebSocketDisconnect:
                    print("Client disconnected")
                    await assemblyai_ws.close()
                except Exception as e:
                    print(f"Error forwarding audio: {e}")
                    await assemblyai_ws.close()

            async def forward_transcripts():
                try:
                    async for message in assemblyai_ws:
                        data = json.loads(message)
                        print("AssemblyAI message:", data)

                        msg_type = data.get("type")

                        if msg_type and msg_type.lower() == "turn":
                            # Send partial update to client
                            transcript = data.get("transcript", "")
                            end_of_turn = data.get("end_of_turn", False)

                            await websocket.send_text(json.dumps({
                                "type": "turn_update",
                                "text": transcript,
                                "end_of_turn": end_of_turn
                            }))

                            # If turn ended, send final turn and optionally stop
                            if end_of_turn:
                                await websocket.send_text(json.dumps({
                                    "type": "turn_end",
                                    "text": transcript
                                }))
                                # Close server websocket connection (auto stop)
                                await websocket.close()
                                break

                        elif msg_type == "session_begin":
                            await websocket.send_text(json.dumps({
                                "type": "session_start",
                                "text": "Session started."
                            }))
                        elif msg_type == "session_terminated":
                            await websocket.send_text(json.dumps({
                                "type": "session_end",
                                "text": "Session terminated by server."
                            }))
                            await websocket.close()
                            break
                        elif msg_type == "Begin":
                            # Initial handshake message, can log or ignore
                            print("Received Begin message from AssemblyAI")
                        else:
                            print(f"Unhandled message type from AssemblyAI: {msg_type}")
                except Exception as e:
                    print(f"Error receiving transcripts: {e}")
                    await websocket.close()

            await asyncio.gather(
                forward_audio(),
                forward_transcripts(),
            )

    except Exception as e:
        print(f"Failed to connect to AssemblyAI WebSocket: {e}")
        await websocket.close()
