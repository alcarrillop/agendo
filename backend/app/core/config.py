"""
Core configuration settings for the Agendo backend.
Handles environment variables and application settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application settings
    APP_NAME: str = "Awendo Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: Optional[str] = "development"
    API_V1_STR: str = "/api/v1"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS settings
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3001"
    ]
    
    # Supabase database settings
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None  # This is the anon key
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    DATABASE_URL: Optional[str] = None
    
    # Evolution API settings (WhatsApp integration)
    EVOLUTION_API_URL: Optional[str] = None
    EVOLUTION_API_KEY: Optional[str] = None
    
    # Google Calendar API settings
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    
    # OpenAI API settings (for LangGraph agent)
    OPENAI_API_KEY: Optional[str] = None
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Webhook settings
    WEBHOOK_SECRET: Optional[str] = None
    WEBHOOK_BASE_URL: Optional[str] = None  # Base URL for webhooks (e.g., https://yourapp.com)
    
    class Config:
        # Load environment variables from .env file
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance."""
    return settings
