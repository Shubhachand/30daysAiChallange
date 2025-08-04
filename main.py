from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

MURF_API_KEY = os.getenv("MURF_API_KEY")

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
