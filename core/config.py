from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AITools Platform"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    JWT_ALGORITHM: str = "HS256"
    # Durée du token selon "Se souvenir de moi"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60       # session normale : 1 heure
    ACCESS_TOKEN_REMEMBER_ME_DAYS: int = 30     # "Se souvenir de moi" : 30 jours

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",   # Next.js dev
        "http://localhost:3001",
        "https://your-domain.com", # Production
    ]

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Database
    DATABASE_URL: str = "postgresql://aitools:aitools@localhost:5432/aitools"

    # File storage
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    ALLOWED_AUDIO_TYPES: List[str] = ["audio/mpeg", "audio/wav", "audio/ogg", "audio/mp4", "video/mp4"]
    ALLOWED_PDF_TYPES: List[str] = ["application/pdf"]

    # Storage backend: "local" or "s3"
    STORAGE_BACKEND: str = "local"
    S3_BUCKET: str = ""
    S3_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Créer les dossiers si inexistants
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
