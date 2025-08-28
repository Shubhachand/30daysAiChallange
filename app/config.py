from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    MURF_API_KEY: str = ""
    ASSEMBLYAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    NEWS_API_KEY: str = ""
    FALLBACK_TEXT: str = "I'm having trouble connecting right now. Please try again later."
    DEFAULT_PERSONA: str = "Teacher"
    AVAILABLE_PERSONAS: list[str] = ["Teacher", "Pirate", "Cowboy", "Robot"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Check for user-provided API keys in environment variables
        # These would be set by the frontend when saving keys
        self.MURF_API_KEY = os.getenv("USER_MURF_API_KEY") or self.MURF_API_KEY
        self.ASSEMBLYAI_API_KEY = os.getenv("USER_ASSEMBLYAI_API_KEY") or self.ASSEMBLYAI_API_KEY
        self.GEMINI_API_KEY = os.getenv("USER_GEMINI_API_KEY") or self.GEMINI_API_KEY
        self.TAVILY_API_KEY = os.getenv("USER_TAVILY_API_KEY") or self.TAVILY_API_KEY
        self.NEWS_API_KEY = os.getenv("USER_NEWS_API_KEY") or self.NEWS_API_KEY

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
