import os
from fastapi import APIRouter, File, UploadFile
from app.utils.files import save_temp_upload
from app.services.stt_assemblyai import stt
from app.services.llm_gemini import llm
from app.services.tts_murf import tts
from app.services.storage import store
from app.config import settings
from app.models.schemas import AgentChatResponse

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/chat/{session_id}", response_model=AgentChatResponse)
async def chat(session_id: str, file: UploadFile = File(...), persona: str = "Teacher"):
    path = await save_temp_upload(file)
    try:
        transcription = stt.transcribe_file(path) or settings.FALLBACK_TEXT
        store.append(session_id, "user", transcription)

        # Build prompt from history
        history = store.history(session_id)
        prompt = "\n".join(
            f"{'User' if m['role']=='user' else 'Assistant'}: {m['content']}"
            for m in history
        )

        # Generate persona-specific prompt
        persona_prompt = llm.generate_persona_prompt(persona, prompt)
        reply = llm.generate(persona_prompt, persona) or settings.FALLBACK_TEXT
        if len(reply) > 3000:
            reply = reply[:2990] + "..."

        store.append(session_id, "assistant", reply)
        audio = tts.synth(reply) or tts.synth(settings.FALLBACK_TEXT)

        return {"transcription": transcription, "response": reply, "audioUrl": audio}
    finally:
        if os.path.exists(path):
            os.remove(path)
