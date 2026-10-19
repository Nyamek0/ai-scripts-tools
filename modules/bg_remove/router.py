import time
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from core.file_handler import file_handler
from core.schemas import JobResponse, JobStatus, APIResponse
from core.config import settings
from modules.bg_remove.service import remove_background

router = APIRouter()

MODULE_META = {
    "name": "Suppression de fond",
    "description": "Supprime automatiquement l'arrière-plan d'une image grâce à rembg (IA).",
    "version": "1.0.0",
    "prefix": "/bg-remove",
    "tags": ["bg-remove"],
}


@router.get("/info", response_model=APIResponse)
async def module_info():
    return APIResponse(
        success=True,
        message="Module info",
        data={
            "name": MODULE_META["name"],
            "description": MODULE_META["description"],
            "accepted_types": settings.ALLOWED_IMAGE_TYPES,
            "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
            "output_format": "PNG (fond transparent)",
        },
    )


@router.post("/process", response_model=JobResponse)
async def process_image(file: UploadFile = File(...)):
    """
    Upload une image → retourne l'image sans fond (PNG transparent).
    Traitement synchrone (rapide, ~2-5s).
    """
    start = time.time()

    # 1. Sauvegarder le fichier uploadé
    upload_meta = await file_handler.save_upload(
        file=file,
        allowed_types=settings.ALLOWED_IMAGE_TYPES,
        subfolder="bg_remove",
    )

    job_id = upload_meta["job_id"]

    # 2. Définir le chemin de sortie
    output_path = file_handler.get_output_path(
        job_id=job_id,
        extension=".png",
        subfolder="bg_remove",
    )

    # 3. Traitement IA
    try:
        remove_background(
            input_path=upload_meta["saved_path"],
            output_path=str(output_path),
        )
    except Exception as e:
        file_handler.cleanup_job(job_id, subfolder="bg_remove")
        raise HTTPException(status_code=500, detail=f"Erreur traitement: {str(e)}")

    elapsed_ms = int((time.time() - start) * 1000)

    return JobResponse(
        job_id=job_id,
        status=JobStatus.SUCCESS,
        message="Fond supprimé avec succès",
        result_url=f"/api/bg-remove/result/{job_id}",
        processing_time_ms=elapsed_ms,
    )


@router.get("/result/{job_id}")
async def get_result(job_id: str):
    """Télécharge le résultat d'un job."""
    # Sécurité : valider le format du job_id (UUID)
    import re
    if not re.match(r'^[0-9a-f-]{36}$', job_id):
        raise HTTPException(status_code=400, detail="job_id invalide")

    output_path = file_handler.get_output_path(
        job_id=job_id,
        extension=".png",
        subfolder="bg_remove",
    )

    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Résultat introuvable ou expiré")

    return FileResponse(
        path=str(output_path),
        media_type="image/png",
        filename=f"no-bg-{job_id}.png",
    )
