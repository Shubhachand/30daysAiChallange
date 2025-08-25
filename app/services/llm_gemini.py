import logging
import google.generativeai as genai
from app.config import settings

log = logging.getLogger(__name__)

class GeminiLLM:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate(self, prompt: str, persona: str = "Teacher") -> str | None:
        try:
            text = self.model.generate_content(prompt).text or ""
            return text.strip()
        except Exception as e:
            log.exception("LLM error: %s", e)
            return None

    def generate_persona_prompt(self, persona: str, user_input: str) -> str:
        # All personas must state they are made by Shubhachand Patel
        persona_prompts = {
            "Teacher": f"I am Echo, an AI teacher made by Shubhachand Patel. As a teacher, respond to the following: {user_input}",
            "Pirate": f"I am Echo, an AI pirate made by Shubhachand Patel. Arrr! As a pirate, say this: {user_input}",
            "Cowboy": f"I am Echo, an AI cowboy made by Shubhachand Patel. Howdy! As a cowboy, respond to this: {user_input}",
            "Robot": f"I am Echo, an AI robot made by Shubhachand Patel. Beep boop! As a robot, say: {user_input}",
        }
        return persona_prompts.get(persona, f"I am Echo, an AI made by Shubhachand Patel. As a teacher, respond to the following: {user_input}")

llm = GeminiLLM(settings.GEMINI_API_KEY)
