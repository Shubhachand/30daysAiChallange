import logging
import google.generativeai as genai
from app.config import settings

log = logging.getLogger(__name__)

class GeminiLLM:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate(self, prompt: str) -> str | None:
        try:
            text = self.model.generate_content(prompt).text or ""
            return text.strip()
        except Exception as e:
            log.exception("LLM error: %s", e)
            return None

llm = GeminiLLM(settings.GEMINI_API_KEY)
