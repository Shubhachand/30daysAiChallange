from app.services.stream_gemini_to_murf import stream_gemini_to_murf
from app.services.llm_gemini import llm
from app.services.storage import store
from app.config import settings
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import os
import json
import websockets
import asyncio
import base64
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

router = APIRouter()


def build_prompt_from_history(history, max_turns=3):
    # Persona and instructions for Echo
    system = (
        "You are Echo, a helpful, friendly, and witty AI assistant made by Shubhachand Patel. "
        "You remember the conversation history and can handle all typical conversational AI commands (e.g., tell a joke, set a reminder, answer questions, summarize, translate, etc). "
        "Always respond as Echo, and keep your answers concise, clear, and engaging."
    )
    prompt = system + "\n"
    # Only use the last max_turns*2 messages (user+assistant pairs)
    if len(history) > max_turns * 2:
        history = history[-max_turns*2:]
    for msg in history:
        role = "User" if msg["role"] == "user" else "Echo"
        prompt += f"{role}: {msg['content']}\n"
    prompt += "Echo:"
    return prompt

@router.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):

    await websocket.accept()
    print("Client connected to /ws/transcribe")

    url = "wss://streaming.assemblyai.com/v3/ws?sample_rate=16000"
    headers = {"Authorization": API_KEY}

    # Use websocket id as session_id
    session_id = str(id(websocket))
    try:
        async with websockets.connect(url, extra_headers=headers) as assemblyai_ws:

            async def forward_audio():
                try:
                    audio_chunks = []  # Array to accumulate base64 chunks on server
                    while True:
                        # Receive binary audio chunk from client
                        audio_chunk = await websocket.receive_bytes()
                        
                        # Convert to base64 and accumulate
                        base64_chunk = base64.b64encode(audio_chunk).decode('utf-8')
                        audio_chunks.append(base64_chunk)
                        print(f"Server Acknowledgement: Audio data received, base64 length: {len(base64_chunk)}")
                        
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

                            # If turn ended, update history, build prompt, and process LLM/Murf
                            if end_of_turn:
                                await websocket.send_text(json.dumps({
                                    "type": "turn_end",
                                    "text": transcript
                                }))
                                # Store user message
                                store.append(session_id, "user", transcript)
                                # Build prompt from history (history already includes latest user message)
                                history = store.history(session_id)
                                prompt = build_prompt_from_history(history)
                                # Generate LLM response (full, for chat bubble)
                                llm_response = llm.generate(prompt) or settings.FALLBACK_TEXT
                                # Store assistant message
                                store.append(session_id, "assistant", llm_response)
                                await websocket.send_text(json.dumps({
                                    "type": "ai_text",
                                    "text": llm_response
                                }))
                                # Stream the stored LLM response to Murf for TTS (no repeated LLM call)
                                await stream_gemini_to_murf(llm_response, websocket)
                                # Do NOT close websocket here; allow for multi-turn conversation

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
