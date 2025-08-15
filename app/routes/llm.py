import os
from fastapi import APIRouter, File, UploadFile
from app.utils.files import save_temp_upload
from app.services.stt_assemblyai import stt
from app.services.llm_gemini import llm
from app.services.tts_murf import tts
from app.config import settings
from app.models.schemas import LlmQueryResponse

router = APIRouter(prefix="/llm", tags=["llm"])

@router.post("/query", response_model=LlmQueryResponse)
async def query(file: UploadFile = File(...)):
    path = await save_temp_upload(file)
    try:
        transcription = stt.transcribe_file(path) or settings.FALLBACK_TEXT
        reply = llm.generate(transcription) or settings.FALLBACK_TEXT
        if len(reply) > 3000:
            reply = reply[:2990] + "..."
        audio = tts.synth(reply) or tts.synth(settings.FALLBACK_TEXT)
        return {"transcription": transcription, "response": reply, "audioUrl": audio}
    finally:
        if os.path.exists(path):
            os.remove(path)
