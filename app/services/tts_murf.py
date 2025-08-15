import logging
import requests
from app.config import settings

log = logging.getLogger(__name__)

class MurfTTS:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://api.murf.ai/v1/speech/generate"

    def synth(self, text: str, voice_id: str = "en-US-natalie", fmt: str = "MP3") -> str | None:
        try:
            headers = {"api-key": self.api_key, "Content-Type": "application/json"}
            payload = {"voiceId": voice_id, "text": text, "format": fmt}
            res = requests.post(self.url, headers=headers, json=payload, timeout=60)
            res.raise_for_status()
            return res.json().get("audioFile")
        except Exception as e:
            log.exception("Murf TTS error: %s", e)
            return None

tts = MurfTTS(settings.MURF_API_KEY)
