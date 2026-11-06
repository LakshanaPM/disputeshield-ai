"""
DisputeShield AI — Application Configuration

Loads all settings from environment variables using Pydantic BaseSettings.
Supports .env files for local development.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- PayPal ---
    paypal_client_id: str = ""
    paypal_client_secret: str = ""
    paypal_environment: str = "SANDBOX"
    paypal_webhook_id: str = ""
    paypal_base_url: str = "https://api-m.sandbox.paypal.com"

    # --- OpenAI ---
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # --- Google Gemini ---
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"


    # --- Database ---
    database_url: str = "postgresql://disputeshield:disputeshield@localhost:5432/disputeshield"

    # --- Elasticsearch ---
    elasticsearch_url: str = "http://localhost:9200"
    elasticsearch_index_disputes: str = "disputes"
    elasticsearch_index_vectors: str = "dispute_vectors"

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- Application ---
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = True
    environment: str = "development"
    app_secret_key: str = "change-this-to-a-random-secret-key"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # --- Agent ---
    agent_auto_submit_threshold: int = 80
    agent_draft_threshold: int = 60
    agent_max_submissions_per_minute: int = 10

    @property
    def is_sandbox(self) -> bool:
        """Check if running in PayPal sandbox mode."""
        return self.paypal_environment.upper() == "SANDBOX"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Singleton settings instance
settings = Settings()
