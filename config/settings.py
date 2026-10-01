"""
Configuration and environment settings for Retail AI Assistant.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # API Keys and Credentials
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Model Configuration
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4-turbo-preview")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2048"))

    # Vector Store Configuration
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./chromadb_data")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    VECTOR_DIMENSION: int = int(os.getenv("VECTOR_DIMENSION", "1536"))

    # Database Configuration
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL", None)

    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Agent Configuration
    AGENT_NAME: str = "Retail AI Assistant"
    AGENT_VERSION: str = "1.0.0"
    MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "10"))
    TIMEOUT_SECONDS: int = int(os.getenv("TIMEOUT_SECONDS", "30"))

    # Retrieval Configuration
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))

    # Cache Configuration
    ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "True").lower() == "true"
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))

    # Feature Flags
    ENABLE_ANALYTICS: bool = os.getenv("ENABLE_ANALYTICS", "True").lower() == "true"
    ENABLE_USER_FEEDBACK: bool = os.getenv("ENABLE_USER_FEEDBACK", "True").lower() == "true"

    @classmethod
    def validate(cls) -> None:
        """Validate required settings."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

    @classmethod
    def to_dict(cls) -> dict:
        """Return settings as dictionary."""
        return {
            k: getattr(cls, k)
            for k in dir(cls)
            if not k.startswith("_") and k.isupper()
        }


# Initialize settings
settings = Settings()
