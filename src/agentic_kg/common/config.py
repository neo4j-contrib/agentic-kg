import logging
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from agentic_kg.common.pydantic_neo4j import Neo4jDsn

class agentic_kgSettings(BaseSettings):
    """Application configuration loaded from environment variables or .env file."""

    # Logging configuration
    loglevel: str = Field(default="INFO")

    # LLM Provider configuration
    openai_api_key: Optional[str] = Field(default=None)
    google_api_key: Optional[str] = Field(default=None)
    gemini_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)

    # LLM Model configuration
    llm_model: Optional[str] = Field(default="openai/gpt-4o")
    llm_base_url: Optional[str] = Field(default=None)

    # Neo4j configuration
    neo4j_dsn: Optional[Neo4jDsn] = Field(default="bolt://localhost:7687")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

# Global settings instance
_settings: Optional[agentic_kgSettings] = None
logger = logging.getLogger(__name__)

def get_settings() -> agentic_kgSettings:
    """Get the application settings singleton, loading and initializing if necessary."""
    global _settings
    if _settings is None:
        _settings = agentic_kgSettings()

    # Configure logging only once to avoid double handlers
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        logging.basicConfig(level=_settings.loglevel.upper())
    
    return _settings


def validate_env():
    """Validate expected environmental variables."""
    settings = get_settings()

    # Validate OpenAI settings
    valid_openai_api_key = (settings.openai_api_key and
                           settings.openai_api_key != 'YOUR_OPENAI_API_KEY')
    logger.info(f"OpenAI API Key set: {'Yes' if valid_openai_api_key else 'No (REPLACE PLACEHOLDER!)'}")

    if not valid_openai_api_key:
        raise ValueError("OpenAI API Key not set or placeholder not replaced.")
