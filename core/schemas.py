from pydantic import BaseModel
from typing import Any, Optional
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class APIResponse(BaseModel):
    """Réponse standard pour tous les endpoints."""
    success: bool
    message: str
    data: Optional[Any] = None


class JobResponse(BaseModel):
    """Réponse pour les jobs asynchrones (Celery)."""
    job_id: str
    status: JobStatus
    message: str
    result_url: Optional[str] = None
    error: Optional[str] = None
    processing_time_ms: Optional[int] = None


class ModuleInfo(BaseModel):
    """Métadonnées d'un module."""
    name: str
    description: str
    version: str
    prefix: str
    accepted_types: Optional[list[str]] = None
    max_file_size_mb: Optional[int] = None
