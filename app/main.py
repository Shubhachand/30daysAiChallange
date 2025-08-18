import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from app.routes import root, tts, llm, agent, websocket_route,audio_transcribe 
from fastapi.responses import HTMLResponse
import os

load_dotenv() 

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
# Logging (structured enough for Cloud logs)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
log = logging.getLogger("app")

app = FastAPI(title="AI Voice Agent", version="0.2.0")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(root.router)
app.include_router(tts.router)
app.include_router(llm.router)
app.include_router(agent.router)
app.include_router(websocket_route.router)
app.include_router(audio_transcribe.router)



@app.get("/test", response_class=HTMLResponse)
async def test_page():
    file_path = os.path.join("static", "index.html")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
