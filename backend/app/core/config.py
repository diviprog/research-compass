"""
Application configuration.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Research Assistant API"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: Optional[str] = None
    DATABASE_ECHO: bool = False
    
    # API Keys
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    
    # Bright Data
    BRIGHT_DATA_API_KEY: Optional[str] = None
    
    # CORS (FRONTEND_URL for production; default for local dev)
    FRONTEND_URL: Optional[str] = "http://localhost:5173"
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174"
    ]

    @property
    def cors_origins_list(self) -> list:
        """Allowed CORS origins: hardcoded localhost list + FRONTEND_URL if set and not already included."""
        origins = list(self.CORS_ORIGINS)
        if self.FRONTEND_URL and self.FRONTEND_URL.rstrip("/") not in [o.rstrip("/") for o in origins]:
            origins.append(self.FRONTEND_URL.rstrip("/"))
        return origins

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

