import time
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from typing import Optional

from core.file_handler import file_handler
from core.schemas import JobResponse, JobStatus, APIResponse
from core.config import settings
from modules.transcribe.service import transcribe_audio

router = APIRouter()

MODULE_META = {
    "name": "Transcription audio",
    "description": "Convertit un fichier audio en texte grâce à OpenAI Whisper (100% local, gratuit).",
    "version": "1.0.0",
    "prefix": "/transcribe",
    "tags": ["transcribe"],
}

SUPPORTED_LANGUAGES = {
    "auto": "Détection automatique",
    "fr": "Français",
    "en": "English",
    "es": "Español",
    "de": "Deutsch",
    "it": "Italiano",
    "pt": "Português",
    "ar": "العربية",
    "zh": "中文",
    "ja": "日本語",
}


@router.get("/info", response_model=APIResponse)
async def module_info():
    return APIResponse(
        success=True,
        message="Module info",
        data={
            "name": MODULE_META["name"],
            "description": MODULE_META["description"],
            "accepted_types": settings.ALLOWED_AUDIO_TYPES,
            "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
            "supported_languages": SUPPORTED_LANGUAGES,
            "output_formats": ["txt", "srt", "json"],
            "models": ["tiny", "base", "small", "medium", "large"],
        },
    )


@router.post("/process", response_model=JobResponse)
async def process_audio(
    file: UploadFile = File(...),
    language: Optional[str] = Form(default="auto"),
    model: Optional[str] = Form(default="base"),
    output_format: Optional[str] = Form(default="txt"),
):
    """
    Upload un fichier audio → retourne la transcription en txt, srt ou json.
    
    - language: code ISO ou 'auto' pour détection automatique
    - model: tiny (rapide) → large (précis, lent)
    - output_format: txt | srt | json
    """
    # Validation
    if model not in ["tiny", "base", "small", "medium", "large"]:
        raise HTTPException(status_code=400, detail=f"Modèle invalide: {model}")
    if output_format not in ["txt", "srt", "json"]:
        raise HTTPException(status_code=400, detail=f"Format invalide: {output_format}")

    start = time.time()

    upload_meta = await file_handler.save_upload(
        file=file,
        allowed_types=settings.ALLOWED_AUDIO_TYPES,
        subfolder="transcribe",
    )

    job_id = upload_meta["job_id"]
    output_path = file_handler.get_output_path(
        job_id=job_id,
        extension=f".{output_format}",
        subfolder="transcribe",
    )

    try:
        transcribe_audio(
            input_path=upload_meta["saved_path"],
            output_path=str(output_path),
            language=None if language == "auto" else language,
            model_name=model,
            output_format=output_format,
        )
    except Exception as e:
        file_handler.cleanup_job(job_id, subfolder="transcribe")
        raise HTTPException(status_code=500, detail=f"Erreur transcription: {str(e)}")

    elapsed_ms = int((time.time() - start) * 1000)

    return JobResponse(
        job_id=job_id,
        status=JobStatus.SUCCESS,
        message="Transcription terminée",
        result_url=f"/api/transcribe/result/{job_id}?format={output_format}",
        processing_time_ms=elapsed_ms,
    )


@router.get("/result/{job_id}")
async def get_result(job_id: str, format: str = "txt"):
    import re
    if not re.match(r'^[0-9a-f-]{36}$', job_id):
        raise HTTPException(status_code=400, detail="job_id invalide")
    if format not in ["txt", "srt", "json"]:
        raise HTTPException(status_code=400, detail="Format invalide")

    output_path = file_handler.get_output_path(
        job_id=job_id,
        extension=f".{format}",
        subfolder="transcribe",
    )

    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Résultat introuvable ou expiré")

    media_types = {"txt": "text/plain", "srt": "text/plain", "json": "application/json"}

    return FileResponse(
        path=str(output_path),
        media_type=media_types[format],
        filename=f"transcription-{job_id}.{format}",
    )
