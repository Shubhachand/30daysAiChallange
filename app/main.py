import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import root, tts, llm, agent

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
