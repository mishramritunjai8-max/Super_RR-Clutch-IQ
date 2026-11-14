"""
SUPER RR — CLUTCH IQ
FastAPI Backend Configuration
"""

import os
from pathlib import Path
from typing import List


class Settings:
    PROJECT_NAME: str = "SUPER RR — CLUTCH IQ: Beyond Statistics"
    PROJECT_SLOGAN: str = "Discovering Players Who Perform Under Pressure"
    API_V1_PREFIX: str = "/api/v1"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Path resolution: safely anchored to the project root
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data" / "processed"
    METRICS_DIR: Path = DATA_DIR / "metrics"
    MODELS_DIR: Path = BASE_DIR / "models" / "phase4"
    
    # CORS Configuration
    # Defaults to allowing all origins (*) in production/cloud, or comma-separated origins via CORS_ORIGINS env var
    _cors_env: str = os.getenv("CORS_ORIGINS", "*")
    CORS_ORIGINS: List[str] = [origin.strip() for origin in _cors_env.split(",") if origin.strip()]


settings = Settings()
