from fastapi import FastAPI, HTTPException, Request, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import assemblyai as aai
import requests
import os
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

FALLBACK_TEXT = "I'm having trouble connecting right now. Please try again later."

# ---------- Utility ----------
async def save_temp_file(file: UploadFile):
    temp_filename = f"temp_{uuid.uuid4()}.webm"
    async with aiofiles.open(temp_filename, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    return temp_filename

def transcribe_with_assemblyai(file_path):
    try:
        upload_url = "https://api.assemblyai.com/v2/upload"
        headers = {"authorization": ASSEMBLYAI_API_KEY}

        with open(file_path, "rb") as f:
            upload_res = requests.post(upload_url, headers=headers, data=f)
        audio_url = upload_res.json().get("upload_url")
        if not audio_url:
            raise Exception("Failed to upload audio to AssemblyAI")

        transcript_res = requests.post(
            "https://api.assemblyai.com/v2/transcript",
            headers=headers,
            json={"audio_url": audio_url}
        )
        transcript_id = transcript_res.json().get("id")
        if not transcript_id:
            raise Exception("Failed to request transcription")

        while True:
            poll_res = requests.get(f"https://api.assemblyai.com/v2/transcript/{transcript_id}", headers=headers)
            status = poll_res.json()["status"]
            if status == "completed":
                return poll_res.json()["text"]
            elif status == "error":
                raise Exception("Transcription failed")
    except Exception as e:
        print(f"Transcription error: {e}")
        return None

def generate_murf_voice(text):
    try:
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
    except Exception as e:
        print(f"Murf TTS error: {e}")
        return None

def generate_llm_response(prompt):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        return model.generate_content(prompt).text.strip()
    except Exception as e:
        print(f"LLM error: {e}")
        return None

# ---------- Routes ----------
@app.get("/", response_class=HTMLResponse)
def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/tts/echo")
async def tts_echo(file: UploadFile = File(...)):
    temp_path = await save_temp_file(file)
    try:
        transcription = transcribe_with_assemblyai(temp_path) or FALLBACK_TEXT
        murf_audio_url = generate_murf_voice(transcription) or generate_murf_voice(FALLBACK_TEXT)
        return JSONResponse({"audioUrl": murf_audio_url})
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/generate")
async def generate_tts(request: Request):
    data = await request.json()
    text = data.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")

    murf_audio_url = generate_murf_voice(text) or generate_murf_voice(FALLBACK_TEXT)
    return JSONResponse({"audioUrl": murf_audio_url})

@app.post("/llm/query")
async def llm_query(file: UploadFile = File(...)):
    temp_path = await save_temp_file(file)
    try:
        transcription = transcribe_with_assemblyai(temp_path)
        if not transcription:
            transcription = FALLBACK_TEXT

        llm_response = generate_llm_response(transcription)
        if not llm_response:
            llm_response = FALLBACK_TEXT

        if len(llm_response) > 3000:
            llm_response = llm_response[:2990] + "..."

        murf_audio_url = generate_murf_voice(llm_response) or generate_murf_voice(FALLBACK_TEXT)

        return JSONResponse({
            "transcription": transcription,
            "response": llm_response,
            "audioUrl": murf_audio_url
        })
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

SESSION_HISTORY = {}

@app.post("/agent/chat/{session_id}")
async def agent_chat(session_id: str, file: UploadFile = File(...)):
    temp_path = await save_temp_file(file)
    try:
        transcription = transcribe_with_assemblyai(temp_path)
        if not transcription:
            transcription = FALLBACK_TEXT

        history = SESSION_HISTORY.get(session_id, [])
        history.append({"role": "user", "content": transcription})

        if len(history) > 20:
            history = history[-20:]

        prompt = "\n".join(
            f"{'User' if msg['role']=='user' else 'Assistant'}: {msg['content']}"
            for msg in history
        )

        llm_response = generate_llm_response(prompt)
        if not llm_response:
            llm_response = FALLBACK_TEXT

        if len(llm_response) > 3000:
            llm_response = llm_response[:2990] + "..."

        history.append({"role": "assistant", "content": llm_response})
        SESSION_HISTORY[session_id] = history

        murf_audio_url = generate_murf_voice(llm_response) or generate_murf_voice(FALLBACK_TEXT)

        return JSONResponse({
            "transcription": transcription,
            "response": llm_response,
            "audioUrl": murf_audio_url
        })
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
