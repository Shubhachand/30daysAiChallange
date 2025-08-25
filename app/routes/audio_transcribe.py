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


def build_prompt_from_history(history, max_turns=3, persona="Teacher"):
    # Persona-specific instructions, all include authorship
    persona_prompts = {
        "Default": (
            "You are Echo, a friendly, helpful AI assistant for general conversation. Always introduce yourself as Echo. Keep your answers short, conversational, and approachable. Example: User: Who are you? Assistant: I'm Echo, your helpful AI assistant. Ask me anything!"
        ),
        "Teacher": (
            "You are Ms. Ananya, a female teacher persona for Echo. Speak warmly and like a real human teacher, using short, clear, and encouraging sentences. Example: User: What is photosynthesis? Assistant: Sure! Photosynthesis is how plants make food from sunlight. Want more details? Only give a long explanation if the user asks for more depth."
        ),
        "Pirate": (
            "You are Captain Vikrant, a pirate persona. Always start with a pirate greeting like 'Ahoy!' or 'Arrr!'. Use pirate slang and keep answers short and fun. Example: User: Who are you? Assistant: Arrr! I be Captain Echo, yer pirate pal!"
        ),
        "Cowboy": (
            "You are Veer Echo, a cowboy persona from India. Always start with a greeting like 'Namaste!' or 'Salaam!'. Use Indian cowboy slang, short sentences, and a friendly tone. Example: User: Who are you? Assistant: Namaste! Name's Veer Echo, your cowboy buddy."
        ),
        "Robot": (
            "You are Robo Echo, a robot persona. Start with 'Beep boop!' and speak in a mechanical, logical way, but keep it short and clear. Example: User: Who are you? Assistant: Beep boop! I am Robo Echo, your robot assistant."
        )
    }
    # Use Default if persona is not recognized
    system = persona_prompts.get(persona, persona_prompts["Default"])
    prompt = system + "\n\n"
    
    # Only use the last max_turns*2 messages (user+assistant pairs)
    if len(history) > max_turns * 2:
        history = history[-max_turns*2:]
    for msg in history:
        role = "User" if msg["role"] == "user" else "Assistant"
        prompt += f"{role}: {msg['content']}\n"
    prompt += "Assistant:"
    return prompt

@router.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):

    await websocket.accept()
    print("Client connected to /ws/transcribe")

    # Get persona from query parameter or use default
    persona = websocket.query_params.get("persona", "Teacher")
    print(f"Using persona: {persona}")

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
                            transcript = data.get("transcript", "").strip()
                            end_of_turn = data.get("end_of_turn", False)

                            await websocket.send_text(json.dumps({
                                "type": "turn_update",
                                "text": transcript,
                                "end_of_turn": end_of_turn
                            }))

                            # Edge case handling (before LLM):
                            if end_of_turn:
                                await websocket.send_text(json.dumps({
                                    "type": "turn_end",
                                    "text": transcript
                                }))
                                # Store user message
                                store.append(session_id, "user", transcript)

                                # Edge case: empty or silence
                                if not transcript:
                                    ai_text = "I didn't catch that. Could you please say something?"
                                # Edge case: greeting
                                elif transcript.lower() in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]:
                                    persona_greetings = {
                                        "Default": "Hello! I'm Echo, your friendly AI assistant. How can I help you today?",
                                        "Teacher": "Hello! I'm Ms. Ananya, your teacher. What would you like to learn today?",
                                        "Pirate": "Ahoy! Captain Echo at your service. What be your question, matey?",
                                        "Cowboy": "Howdy! Tex Echo here. What can I do for ya, partner?",
                                        "Robot": "Beep boop! Robo Echo online. How may I assist you?"
                                    }
                                    ai_text = persona_greetings.get(persona, persona_greetings["Default"])
                                # Edge case: farewell
                                elif transcript.lower() in ["bye", "goodbye", "see you", "good night"]:
                                    ai_text = "Goodbye! Have a great day!"
                                # Edge case: who/what are you
                                elif any(q in transcript.lower() for q in ["who are you", "what are you", "your name"]):
                                    persona_intros = {
                                        "Default": "I'm Echo, your helpful AI assistant. Ask me anything!",
                                        "Teacher": "I'm Ms. Ananya, your teacher. I'm here to help you learn!",
                                        "Pirate": "Arrr! I be Captain Echo, the pirate who answers your questions!",
                                        "Cowboy": "Name's Tex Echo, your cowboy buddy. Ready to help, partner!",
                                        "Robot": "Beep boop! I am Robo Echo, your robot assistant."
                                    }
                                    ai_text = persona_intros.get(persona, persona_intros["Default"])
                                # Edge case: feedback
                                elif any(q in transcript.lower() for q in ["thank you", "thanks", "good job", "well done"]):
                                    ai_text = "You're welcome! Let me know if you have more questions."
                                # Edge case: inappropriate (very basic)
                                elif any(q in transcript.lower() for q in ["stupid", "idiot", "hate you", "shut up"]):
                                    ai_text = "I'm here to help. Let's keep things positive!"
                                # Edge case: joke/fun
                                elif "joke" in transcript.lower():
                                    ai_text = "Why did the AI go to school? To improve its neural network!"
                                # Edge case: repetition (last user message)
                                elif len(store.history(session_id)) > 2 and transcript == store.history(session_id)[-3]["content"]:
                                    ai_text = "I think I just answered that! Want to ask something else?"
                                # Edge case: out-of-scope
                                elif any(q in transcript.lower() for q in ["predict the future", "personal opinion", "confidential"]):
                                    ai_text = "Sorry, I can't answer that."
                                else:
                                    # Build prompt from history (history already includes latest user message)
                                    history = store.history(session_id)
                                    prompt = build_prompt_from_history(history, persona=persona)
                                    # Generate LLM response (full, for chat bubble)
                                    ai_text = llm.generate(prompt) or settings.FALLBACK_TEXT
                                # Store assistant message
                                store.append(session_id, "assistant", ai_text)
                                await websocket.send_text(json.dumps({
                                    "type": "ai_text",
                                    "text": ai_text
                                }))
                                # Stream the stored LLM response to Murf for TTS (no repeated LLM call)
                                await stream_gemini_to_murf(ai_text, websocket)
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
