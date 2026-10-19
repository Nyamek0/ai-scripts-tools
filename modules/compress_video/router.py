import time
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from typing import Optional

from core.file_handler import file_handler
from core.schemas import JobResponse, JobStatus, APIResponse
from core.config import settings
from modules.compress_video.service import compress_video

router = APIRouter()

MODULE_META = {
    "name": "Compression vidéo",
    "description": "Compresse une vidéo en réduisant son poids sans perte de qualité visible (ffmpeg H.264).",
    "version": "1.0.0",
    "prefix": "/compress-video",
    "tags": ["compress-video"],
}

ALLOWED_VIDEO_TYPES = [
    "video/mp4",
    "video/x-msvideo",   # .avi
    "video/quicktime",   # .mov
    "video/x-matroska",  # .mkv
    "video/webm",
]

QUALITY_PRESETS = ["high", "medium", "low"]


@router.get("/info", response_model=APIResponse)
async def module_info():
    return APIResponse(
        success=True,
        message="Module info",
        data={
            "name": MODULE_META["name"],
            "description": MODULE_META["description"],
            "accepted_types": ALLOWED_VIDEO_TYPES,
            "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
            "quality_presets": {
                "high": "CRF 20 — qualité maximale, compression modérée",
                "medium": "CRF 28 — bon équilibre qualité/poids (défaut)",
                "low": "CRF 35 — compression maximale, qualité réduite",
            },
            "output_format": "MP4 (H.264 + AAC)",
            "requires": "ffmpeg installé sur le système",
        },
    )


@router.post("/process", response_model=JobResponse)
async def process_video(
    file: UploadFile = File(...),
    quality: Optional[str] = Form(default="medium"),
):
    """
    Upload une vidéo → retourne la vidéo compressée en MP4.

    - quality: high | medium | low
    """
    if quality not in QUALITY_PRESETS:
        raise HTTPException(
            status_code=400,
            detail=f"Qualité invalide: {quality}. Options: {QUALITY_PRESETS}",
        )

    start = time.time()

    upload_meta = await file_handler.save_upload(
        file=file,
        allowed_types=ALLOWED_VIDEO_TYPES,
        subfolder="compress_video",
    )

    job_id = upload_meta["job_id"]
    output_path = file_handler.get_output_path(
        job_id=job_id,
        extension=".mp4",
        subfolder="compress_video",
    )

    try:
        result = compress_video(
            input_path=upload_meta["saved_path"],
            output_path=str(output_path),
            quality=quality,
        )
    except Exception as e:
        file_handler.cleanup_job(job_id, subfolder="compress_video")
        raise HTTPException(status_code=500, detail=f"Erreur compression: {str(e)}")
    finally:
        try:
            Path(upload_meta["saved_path"]).unlink(missing_ok=True)
        except Exception:
            pass

    elapsed_ms = int((time.time() - start) * 1000)
    input_kb = upload_meta["size_bytes"] // 1024
    output_kb = result["output_size_bytes"] // 1024
    reduction = round((1 - result["output_size_bytes"] / upload_meta["size_bytes"]) * 100, 1)

    return JobResponse(
        job_id=job_id,
        status=JobStatus.SUCCESS,
        message=f"Vidéo compressée ({input_kb}KB → {output_kb}KB, -{reduction}%)",
        result_url=f"/api/compress-video/result/{job_id}",
        processing_time_ms=elapsed_ms,
    )


@router.get("/result/{job_id}")
async def get_result(job_id: str):
    import re
    if not re.match(r'^[0-9a-f-]{36}$', job_id):
        raise HTTPException(status_code=400, detail="job_id invalide")

    output_path = file_handler.get_output_path(
        job_id=job_id,
        extension=".mp4",
        subfolder="compress_video",
    )

    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Résultat introuvable ou expiré")

    return FileResponse(
        path=str(output_path),
        media_type="video/mp4",
        filename=f"compressed-{job_id}.mp4",
    )
