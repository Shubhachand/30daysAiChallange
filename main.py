from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

MURF_API_KEY = os.getenv("MURF_API_KEY")

class TTSRequest(BaseModel):
    text: str

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
