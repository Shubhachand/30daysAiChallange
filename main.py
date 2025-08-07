from fastapi import FastAPI, HTTPException, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import assemblyai as aai
import requests
import os
import shutil
from dotenv import load_dotenv

load_dotenv()


MURF_API_KEY = os.getenv("MURF_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
aai.settings.api_key = ASSEMBLYAI_API_KEY


app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class TTSRequest(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate")
def generate_tts(data: TTSRequest):
    url = "https://api.murf.ai/v1/speech/generate"
    headers = {
        "api-key": MURF_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": data.text,
        "voiceId": "en-US-natalie",
        "modelVersion": "GEN2",
        "format": "MP3"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()
        return {
            "audioUrl": result.get("audioFile"),
            "length": result.get("audioLengthInSeconds"),
            "charsUsed": result.get("consumedCharacterCount")
        }
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    try:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "size_in_kb": round(os.path.getsize(file_location) / 1024, 2)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/transcribe/file")
def transcribe_file(file: UploadFile = File(...)):
    try:
        audio_data = file.file.read()
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_data)

        return {
            "text": transcript.text,
            "confidence": transcript.words[0].confidence if transcript.words else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
