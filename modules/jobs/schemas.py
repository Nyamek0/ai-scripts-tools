import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Job ───────────────────────────────────────────────────────────────────────

class JobOut(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    module_name: str
    status: str
    input_filename: Optional[str]
    input_size_bytes: Optional[int]
    result_url: Optional[str]
    output_size_bytes: Optional[int]
    error_message: Optional[str]
    processing_time_ms: Optional[int]
    created_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class JobListParams(BaseModel):
    """Paramètres de filtrage/pagination pour lister les jobs."""
    module_name: Optional[str] = None
    status: Optional[str] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class JobListResponse(BaseModel):
    jobs: list[JobOut]
    total: int
    page: int
    per_page: int
    pages: int


# ── Stats ─────────────────────────────────────────────────────────────────────

class ModuleStatOut(BaseModel):
    module_name: str
    total_jobs: int
    successful_jobs: int
    failed_jobs: int
    total_processing_time_ms: int
    avg_processing_time_ms: int
    success_rate: float
    last_used_at: Optional[datetime]

    model_config = {"from_attributes": True}


class PlatformStatsOut(BaseModel):
    """Stats globales de la plateforme."""
    total_users: int
    total_jobs: int
    total_successful: int
    total_failed: int
    modules: list[ModuleStatOut]
