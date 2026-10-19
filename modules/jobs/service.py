import logging
import math
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from modules.jobs.models import Job, ModuleStat

logger = logging.getLogger(__name__)


# ── CRUD Jobs ─────────────────────────────────────────────────────────────────

async def create_job(
    db: AsyncSession,
    module_name: str,
    user_id: Optional[UUID] = None,
    input_filename: Optional[str] = None,
    input_size_bytes: Optional[int] = None,
) -> Job:
    """Crée un job avec statut 'processing'."""
    job = Job(
        module_name=module_name,
        user_id=user_id,
        status="processing",
        input_filename=input_filename,
        input_size_bytes=input_size_bytes,
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)
    return job


async def complete_job(
    db: AsyncSession,
    job_id: UUID,
    result_url: Optional[str] = None,
    output_size_bytes: Optional[int] = None,
    processing_time_ms: Optional[int] = None,
) -> Job:
    """Marque un job comme réussi et met à jour les stats du module."""
    job = await db.get(Job, job_id)
    if not job:
        raise ValueError(f"Job introuvable: {job_id}")

    job.status = "success"
    job.result_url = result_url
    job.output_size_bytes = output_size_bytes
    job.processing_time_ms = processing_time_ms
    job.completed_at = datetime.now(timezone.utc)

    await _update_module_stat(db, job.module_name, success=True,
                              processing_time_ms=processing_time_ms)
    await db.flush()
    return job


async def fail_job(
    db: AsyncSession,
    job_id: UUID,
    error_message: str,
    processing_time_ms: Optional[int] = None,
) -> Job:
    """Marque un job comme échoué et met à jour les stats du module."""
    job = await db.get(Job, job_id)
    if not job:
        raise ValueError(f"Job introuvable: {job_id}")

    job.status = "failed"
    job.error_message = error_message
    job.processing_time_ms = processing_time_ms
    job.completed_at = datetime.now(timezone.utc)

    await _update_module_stat(db, job.module_name, success=False,
                              processing_time_ms=processing_time_ms)
    await db.flush()
    return job


async def get_job(db: AsyncSession, job_id: UUID) -> Optional[Job]:
    return await db.get(Job, job_id)


async def list_jobs(
    db: AsyncSession,
    user_id: Optional[UUID] = None,
    module_name: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Job], int]:
    """
    Liste les jobs avec filtrage et pagination.
    Retourne (jobs, total_count).
    """
    query = select(Job)
    count_query = select(func.count(Job.id))

    if user_id is not None:
        query = query.where(Job.user_id == user_id)
        count_query = count_query.where(Job.user_id == user_id)
    if module_name:
        query = query.where(Job.module_name == module_name)
        count_query = count_query.where(Job.module_name == module_name)
    if status:
        query = query.where(Job.status == status)
        count_query = count_query.where(Job.status == status)

    total = (await db.execute(count_query)).scalar_one()

    query = query.order_by(Job.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(query)
    jobs = list(result.scalars().all())

    return jobs, total


# ── Stats modules ─────────────────────────────────────────────────────────────

async def _update_module_stat(
    db: AsyncSession,
    module_name: str,
    success: bool,
    processing_time_ms: Optional[int] = None,
) -> None:
    """Met à jour (ou crée) les stats agrégées d'un module."""
    result = await db.execute(
        select(ModuleStat).where(ModuleStat.module_name == module_name)
    )
    stat = result.scalar_one_or_none()

    if stat is None:
        stat = ModuleStat(module_name=module_name)
        db.add(stat)

    stat.total_jobs += 1
    if success:
        stat.successful_jobs += 1
    else:
        stat.failed_jobs += 1
    if processing_time_ms:
        stat.total_processing_time_ms += processing_time_ms
    stat.last_used_at = datetime.now(timezone.utc)


async def get_all_module_stats(db: AsyncSession) -> list[ModuleStat]:
    result = await db.execute(
        select(ModuleStat).order_by(ModuleStat.total_jobs.desc())
    )
    return list(result.scalars().all())


async def get_platform_stats(db: AsyncSession) -> dict:
    """Stats globales de la plateforme (pour le dashboard admin)."""
    from modules.auth.models import User

    total_users = (await db.execute(select(func.count(User.id)))).scalar_one()
    total_jobs = (await db.execute(select(func.count(Job.id)))).scalar_one()
    total_ok = (await db.execute(
        select(func.count(Job.id)).where(Job.status == "success")
    )).scalar_one()
    total_ko = (await db.execute(
        select(func.count(Job.id)).where(Job.status == "failed")
    )).scalar_one()

    module_stats = await get_all_module_stats(db)

    return {
        "total_users": total_users,
        "total_jobs": total_jobs,
        "total_successful": total_ok,
        "total_failed": total_ko,
        "modules": module_stats,
    }
