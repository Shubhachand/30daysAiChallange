from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MURF_API_KEY: str
    ASSEMBLYAI_API_KEY: str
    GEMINI_API_KEY: str
    TAVILY_API_KEY: str
    FALLBACK_TEXT: str = "I'm having trouble connecting right now. Please try again later."
    DEFAULT_PERSONA: str = "Teacher"
    AVAILABLE_PERSONAS: list[str] = ["Teacher", "Pirate", "Cowboy", "Robot"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
