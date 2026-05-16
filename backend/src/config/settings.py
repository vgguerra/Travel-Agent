"""Configurações do projeto usando pydantic-settings para validação de tipos."""
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class _Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    OPENWEATHER_API_KEY: str
    RAPID_KEY: str
    RAPID_HOST: str = "booking-com15.p.rapidapi.com"

    LLM_PROVIDER: str = "google"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 2048

    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b"

    GOOGLE_API_KEY: str = ""
    GOOGLE_MODEL: str = "gemini-2.0-flash"

    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "arcee-ai/trinity-large-thinking:free"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    SUPABASE_URL: str
    SUPABASE_PASSWORD: str
    SUPABASE_JWT_SECRET: str
    SUPABASE_ANON_KEY: str = ""

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True


settings = _Settings()
