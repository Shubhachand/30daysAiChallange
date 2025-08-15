import logging
import requests
from app.config import settings

log = logging.getLogger(__name__)

class AssemblyAITranscriber:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base = "https://api.assemblyai.com/v2"

    def transcribe_file(self, path: str) -> str | None:
        try:
            headers = {"authorization": self.api_key}
            with open(path, "rb") as f:
                up = requests.post(f"{self.base}/upload", headers=headers, data=f, timeout=60)
            up.raise_for_status()
            audio_url = up.json().get("upload_url")
            if not audio_url:
                raise RuntimeError("No upload_url from AssemblyAI")

            req = requests.post(f"{self.base}/transcript", headers=headers, json={"audio_url": audio_url}, timeout=30)
            req.raise_for_status()
            tid = req.json().get("id")
            if not tid:
                raise RuntimeError("No transcript id from AssemblyAI")

            # poll
            while True:
                poll = requests.get(f"{self.base}/transcript/{tid}", headers=headers, timeout=30)
                poll.raise_for_status()
                js = poll.json()
                status = js.get("status")
                if status == "completed":
                    return js.get("text", "")
                if status == "error":
                    log.error("AssemblyAI error: %s", js.get("error"))
                    return None
        except Exception as e:
            log.exception("Transcription error: %s", e)
            return None

stt = AssemblyAITranscriber(settings.ASSEMBLYAI_API_KEY)
