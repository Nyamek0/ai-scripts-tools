import math
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.schemas import APIResponse
from modules.auth.dependencies import get_current_user, get_current_user_optional
from modules.auth.models import User
from modules.jobs.schemas import (
    JobOut, JobListResponse, ModuleStatOut, PlatformStatsOut,
)
from modules.jobs.service import (
    get_job, list_jobs, get_all_module_stats, get_platform_stats,
)

router = APIRouter()

MODULE_META = {
    "name": "Jobs & Statistiques",
    "description": "Historique des traitements et statistiques d'utilisation de la plateforme.",
    "version": "1.0.0",
    "prefix": "/jobs",
    "tags": ["jobs"],
}


# ── Mes jobs ──────────────────────────────────────────────────────────────────

@router.get("/mine", response_model=JobListResponse, summary="Mes jobs")
async def my_jobs(
    module_name: Optional[str] = Query(None, description="Filtrer par module"),
    status: Optional[str] = Query(None, description="Filtrer par statut"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Liste les jobs de l'utilisateur connecté (paginé, filtrable)."""
    jobs, total = await list_jobs(
        db=db,
        user_id=current_user.id,
        module_name=module_name,
        status=status,
        page=page,
        per_page=per_page,
    )
    return JobListResponse(
        jobs=[JobOut.model_validate(j) for j in jobs],
        total=total,
        page=page,
        per_page=per_page,
        pages=max(1, math.ceil(total / per_page)),
    )


@router.get("/mine/{job_id}", response_model=JobOut, summary="Détail d'un de mes jobs")
async def my_job_detail(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retourne le détail d'un job appartenant à l'utilisateur connecté."""
    job = await get_job(db, job_id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job introuvable")
    return JobOut.model_validate(job)


# ── Stats publiques ───────────────────────────────────────────────────────────

@router.get("/stats/modules", response_model=list[ModuleStatOut], summary="Stats par module")
async def module_stats(db: AsyncSession = Depends(get_db)):
    """Retourne les statistiques d'utilisation de chaque module (public)."""
    stats = await get_all_module_stats(db)
    result = []
    for s in stats:
        avg = s.total_processing_time_ms // s.total_jobs if s.total_jobs > 0 else 0
        rate = round(s.successful_jobs / s.total_jobs * 100, 1) if s.total_jobs > 0 else 0.0
        result.append(ModuleStatOut(
            module_name=s.module_name,
            total_jobs=s.total_jobs,
            successful_jobs=s.successful_jobs,
            failed_jobs=s.failed_jobs,
            total_processing_time_ms=s.total_processing_time_ms,
            avg_processing_time_ms=avg,
            success_rate=rate,
            last_used_at=s.last_used_at,
        ))
    return result


# ── Dashboard admin ───────────────────────────────────────────────────────────

@router.get("/stats/platform", response_model=PlatformStatsOut, summary="Stats globales (admin)")
async def platform_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Stats globales de la plateforme. Réservé aux super-admins."""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")

    data = await get_platform_stats(db)
    modules_out = []
    for s in data["modules"]:
        avg = s.total_processing_time_ms // s.total_jobs if s.total_jobs > 0 else 0
        rate = round(s.successful_jobs / s.total_jobs * 100, 1) if s.total_jobs > 0 else 0.0
        modules_out.append(ModuleStatOut(
            module_name=s.module_name,
            total_jobs=s.total_jobs,
            successful_jobs=s.successful_jobs,
            failed_jobs=s.failed_jobs,
            total_processing_time_ms=s.total_processing_time_ms,
            avg_processing_time_ms=avg,
            success_rate=rate,
            last_used_at=s.last_used_at,
        ))

    return PlatformStatsOut(
        total_users=data["total_users"],
        total_jobs=data["total_jobs"],
        total_successful=data["total_successful"],
        total_failed=data["total_failed"],
        modules=modules_out,
    )


# ── Admin : tous les jobs ────────────────────────────────────────────────────

@router.get("/all", response_model=JobListResponse, summary="Tous les jobs (admin)")
async def all_jobs(
    module_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Liste tous les jobs de la plateforme. Réservé aux super-admins."""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")

    jobs, total = await list_jobs(
        db=db,
        module_name=module_name,
        status=status,
        page=page,
        per_page=per_page,
    )
    return JobListResponse(
        jobs=[JobOut.model_validate(j) for j in jobs],
        total=total,
        page=page,
        per_page=per_page,
        pages=max(1, math.ceil(total / per_page)),
    )
