from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application-wide configuration sourced from environment variables."""

    OLLAMA_BASE_URL: str = Field("http://localhost:11434", description="Base URL for the Ollama server")
    OLLAMA_MODEL: str = Field("qwen2.5-coder:7b", description="Model name to load with Ollama")
    MAX_ITERATIONS: int = Field(5, description="Maximum graph iterations before stopping")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
