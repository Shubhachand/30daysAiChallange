from fastapi import FastAPI, HTTPException, Request, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import assemblyai as aai
import requests
import os
import shutil
import uuid
import aiofiles
import google.generativeai as genai 
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

MURF_API_KEY = os.getenv("MURF_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
# Home route
@app.get("/", response_class=HTMLResponse)
def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Save uploaded audio temporarily
async def save_temp_file(file: UploadFile):
    temp_filename = f"temp_{uuid.uuid4()}.webm"
    async with aiofiles.open(temp_filename, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    return temp_filename

# Transcribe audio with AssemblyAI
def transcribe_with_assemblyai(file_path):
    upload_url = "https://api.assemblyai.com/v2/upload"
    headers = {"authorization": ASSEMBLYAI_API_KEY}

    with open(file_path, "rb") as f:
        upload_res = requests.post(upload_url, headers=headers, data=f)
    audio_url = upload_res.json()["upload_url"]

    transcript_res = requests.post(
        "https://api.assemblyai.com/v2/transcript",
        headers=headers,
        json={"audio_url": audio_url}
    )
    transcript_id = transcript_res.json()["id"]

    while True:
        poll_res = requests.get(f"https://api.assemblyai.com/v2/transcript/{transcript_id}", headers=headers)
        status = poll_res.json()["status"]
        if status == "completed":
            return poll_res.json()["text"]
        elif status == "error":
            raise Exception("Transcription failed")

# Generate Murf AI voice
def generate_murf_voice(text):
    url = "https://api.murf.ai/v1/speech/generate"
    headers = {
        "api-key": MURF_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "voiceId": "en-US-natalie",
        "text": text,
        "format": "MP3"
    }
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code != 200:
        raise Exception(f"Murf API error: {res.text}")
    return res.json()["audioFile"]

# Echo Bot v2 Endpoint
@app.post("/tts/echo")
async def tts_echo(file: UploadFile = File(...)):
    temp_path = await save_temp_file(file)
    try:
        transcription = transcribe_with_assemblyai(temp_path)
        murf_audio_url = generate_murf_voice(transcription)
        return JSONResponse({"audioUrl": murf_audio_url})
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/generate")
async def generate_tts(request: Request):
    data = await request.json()
    text = data.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    try:
        murf_audio_url = generate_murf_voice(text)
        return JSONResponse({"audioUrl": murf_audio_url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.post("/llm/query")
async def llm_query(request: Request):
    data = await request.json()
    text = data.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(text)
        return JSONResponse({"response": response.text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))