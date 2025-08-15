from pydantic import BaseModel

class GenerateTtsRequest(BaseModel):
    text: str

class TtsResponse(BaseModel):
    audioUrl: str | None

class LlmQueryResponse(BaseModel):
    transcription: str
    response: str
    audioUrl: str | None

class AgentChatResponse(LlmQueryResponse):
    pass
