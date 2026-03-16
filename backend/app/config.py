"""
Application Configuration Settings

Loads environment variables and provides configuration for the application.
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "sqlite:///./covid_data.db"
    
    # API
    API_KEY: str = "covid_dashboard_api_key_2024"
    LOG_LEVEL: str = "INFO"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Data Source URLs
    JHU_BASE_URL: str = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data"
    OWID_BASE_URL: str = "https://ourworldindata.org"
    
    # ML Model Configuration
    PREDICTION_DAYS: int = 30
    MODEL_TYPE: str = "linear_regression"
    
    # Cache Configuration
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
