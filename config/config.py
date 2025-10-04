"""
Type-safe configuration classes for Flask application.
Supports different environments with validation using Pydantic.
"""

import os
import logging
from typing import Optional, Literal
from pydantic import field_validator, Field
from pydantic_settings import BaseSettings
from pathlib import Path


class BaseConfig(BaseSettings):
    """Base configuration with common settings."""
    
    # Flask settings
    SECRET_KEY: str = Field(default_factory=lambda: os.urandom(32).hex())
    FLASK_ENV: Literal["development", "testing", "production"] = "development"
    DEBUG: bool = False
    TESTING: bool = False
    
    # API settings
    API_TITLE: str = "Asteroid Impact Simulator API"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # CORS settings
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # External API settings
    NASA_API_KEY: Optional[str] = None
    NASA_NEO_BASE_URL: str = "https://api.nasa.gov/neo/rest/v1"
    USGS_API_BASE_URL: str = "https://earthquake.usgs.gov/fdsnws"
    WORLDPOP_API_BASE_URL: str = "https://www.worldpop.org/rest"
    
    # Database settings (for future caching)
    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = None
    LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # Performance settings
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB
    REQUEST_TIMEOUT: int = 30  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @field_validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Validate log level is a valid logging level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()
    
    @field_validator("LOG_FILE")
    def validate_log_file(cls, v):
        """Ensure log file directory exists."""
        if v:
            log_path = Path(v)
            log_path.parent.mkdir(parents=True, exist_ok=True)
        return v


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""
    
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    LOG_FILE: str = "logs/development.log"
    
    # Development-specific settings
    FLASK_ENV: Literal["development", "testing", "production"] = "development"
    CORS_ORIGINS: list[str] = ["*"]  # Allow all origins in development


class TestingConfig(BaseConfig):
    """Testing environment configuration."""
    
    TESTING: bool = True
    DEBUG: bool = True
    LOG_LEVEL: str = "WARNING"
    
    # Testing-specific settings
    FLASK_ENV: Literal["development", "testing", "production"] = "testing"
    DATABASE_URL: str = "sqlite:///:memory:"
    
    # Disable external API calls in testing
    NASA_API_KEY: Optional[str] = "test_key"


class ProductionConfig(BaseConfig):
    """Production environment configuration."""
    
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/production.log"
    
    # Production-specific settings
    FLASK_ENV: Literal["development", "testing", "production"] = "production"
    
    @field_validator("SECRET_KEY")
    def validate_secret_key_in_production(cls, v):
        """Ensure secret key is properly set in production."""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters in production")
        return v
    
    @field_validator("NASA_API_KEY")
    def validate_nasa_api_key_in_production(cls, v):
        """Ensure NASA API key is set in production."""
        if not v:
            raise ValueError("NASA_API_KEY is required in production")
        return v


# Configuration factory
def get_config() -> BaseConfig:
    """Get configuration based on FLASK_ENV environment variable."""
    env = os.getenv("FLASK_ENV", "development").lower()
    
    config_map = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }
    
    config_class = config_map.get(env, DevelopmentConfig)
    return config_class()


# Global config instance
config = get_config()