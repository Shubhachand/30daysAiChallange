import os
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.utils.files import save_temp_upload
from app.services.stt_assemblyai import stt
from app.services.tts_murf import tts
from app.config import settings
from app.models.schemas import GenerateTtsRequest, TtsResponse

router = APIRouter(prefix="/tts", tags=["tts"])

@router.post("/echo", response_model=TtsResponse)
async def echo(file: UploadFile = File(...)):
    path = await save_temp_upload(file)
    try:
        text = stt.transcribe_file(path) or settings.FALLBACK_TEXT
        audio = tts.synth(text) or tts.synth(settings.FALLBACK_TEXT)
        return {"audioUrl": audio}
    finally:
        if os.path.exists(path):
            os.remove(path)

@router.post("/generate", response_model=TtsResponse)
async def generate(req: GenerateTtsRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    audio = tts.synth(req.text) or tts.synth(settings.FALLBACK_TEXT)
    return {"audioUrl": audio}
