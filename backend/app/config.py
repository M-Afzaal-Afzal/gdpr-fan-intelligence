"""Application configuration loaded from environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed settings; all secrets live in env vars only."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    ENVIRONMENT: str = "development"
    FRONTEND_ORIGIN: str = "http://localhost:3000"

    # PostgreSQL — keep psycopg v3 driver string.
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/fan_intelligence"

    # LLM
    # "stub" | "openai" | "gemini" | "anthropic" | "ollama" | "huggingface" | "fireworks"
    LLM_PROVIDER: str = "stub"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"

    # Gemini (Google)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"

    # Anthropic/Claude
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-haiku-20240307"
    ANTHROPIC_BASE_URL: str = "https://api.anthropic.com/v1"

    # Ollama (local open-source)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    # HuggingFace Inference API
    HF_API_KEY: str = ""
    HF_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.3"
    HF_BASE_URL: str = "https://api-inference.huggingface.co/models"

    # Fireworks AI (OpenAI-compatible)
    FIREWORKS_API_KEY: str = ""
    FIREWORKS_MODEL: str = "accounts/fireworks/models/llama-v3p1-70b-instruct"
    FIREWORKS_BASE_URL: str = "https://api.fireworks.ai/inference/v1"

    # Pipeline behaviour
    MAX_MESSAGE_LENGTH: int = 5000
    MIN_MESSAGE_LENGTH: int = 5


settings = Settings()
