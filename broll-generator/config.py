"""
Configuration for Hyperlocal B-Roll Generator
Environment variables and settings
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # App settings
    app_name: str = "Hyperlocal B-Roll Generator"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # Google API Keys
    google_places_api_key: str = ""
    google_streetview_api_key: str = ""
    google_veo_api_key: str = ""

    # Nanobanana Pro API
    nanobanana_api_key: str = ""
    nanobanana_base_url: str = "https://api.nanobanana.pro/v1"

    # Generation defaults
    default_num_clips: int = 5
    default_search_radius: int = 3000  # meters
    max_concurrent_requests: int = 3
    clip_duration_seconds: float = 5.0

    # Output settings
    output_resolution: str = "1920x1080"
    output_fps: int = 24

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create global settings instance
settings = Settings()


def get_api_keys() -> dict:
    """Get all API keys (for validation)"""
    return {
        "google_places": settings.google_places_api_key,
        "google_streetview": settings.google_streetview_api_key,
        "google_veo": settings.google_veo_api_key,
        "nanobanana": settings.nanobanana_api_key
    }


def validate_api_keys() -> dict:
    """Validate that all required API keys are set"""
    keys = get_api_keys()
    status = {}

    for name, key in keys.items():
        status[name] = "configured" if key else "missing"

    return status
