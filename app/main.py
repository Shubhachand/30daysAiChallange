import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from app.routes import root, tts, llm, agent, websocket_route, audio_transcribe 
from fastapi.responses import HTMLResponse
import os
import json

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

# API endpoint to save user-provided API keys
@app.post("/api/save-api-keys")
async def save_api_keys(request: Request):
    try:
        # Get the JSON data from the request
        data = await request.json()
        
        # Set the API keys as environment variables
        os.environ["USER_MURF_API_KEY"] = data.get("MURF_API_KEY", "")
        os.environ["USER_ASSEMBLYAI_API_KEY"] = data.get("ASSEMBLYAI_API_KEY", "")
        os.environ["USER_GEMINI_API_KEY"] = data.get("GEMINI_API_KEY", "")
        os.environ["USER_TAVILY_API_KEY"] = data.get("TAVILY_API_KEY", "")
        os.environ["USER_NEWS_API_KEY"] = data.get("NEWS_API_KEY", "")
        
        # Update the Tavily API key in the web search service
        from app.services.web_search import web_search
        if data.get("TAVILY_API_KEY"):
            web_search.update_api_key(data.get("TAVILY_API_KEY"))
        
        return {"message": "API keys saved successfully"}
    except Exception as e:
        log.error(f"Error saving API keys: {e}")
        return {"error": "Failed to save API keys"}, 500

@app.get("/test", response_class=HTMLResponse)
async def test_page():
    file_path = os.path.join("static", "index.html")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
