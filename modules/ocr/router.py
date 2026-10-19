import time
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

from core.file_handler import file_handler
from core.schemas import JobResponse, JobStatus, APIResponse
from core.config import settings
from modules.ocr.service import extract_text

router = APIRouter()

MODULE_META = {
    "name": "OCR — Image vers texte",
    "description": "Extrait le texte d'une image ou screenshot (EasyOCR, multi-langues).",
    "version": "1.0.0",
    "prefix": "/ocr",
    "tags": ["ocr"],
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
            "supported_languages": ["fr", "en", "es", "de", "it", "pt", "ar", "zh", "ja", "ko"],
        },
    )


@router.post("/process", response_model=APIResponse)
async def process_image(
    file: UploadFile = File(...),
    languages: Optional[str] = Form(default="fr,en"),
):
    """
    Upload une image → retourne le texte extrait.
    languages: liste de codes ISO séparés par virgule (ex: "fr,en")
    """
    start = time.time()

    lang_list = [l.strip() for l in languages.split(",") if l.strip()]
    if not lang_list:
        lang_list = ["fr", "en"]

    upload_meta = await file_handler.save_upload(
        file=file,
        allowed_types=settings.ALLOWED_IMAGE_TYPES,
        subfolder="ocr",
    )

    job_id = upload_meta["job_id"]

    try:
        extracted = extract_text(
            input_path=upload_meta["saved_path"],
            languages=lang_list,
        )
    except Exception as e:
        file_handler.cleanup_job(job_id, subfolder="ocr")
        raise HTTPException(status_code=500, detail=f"Erreur OCR: {str(e)}")
    finally:
        file_handler.cleanup_job(job_id, subfolder="ocr")

    elapsed_ms = int((time.time() - start) * 1000)

    return APIResponse(
        success=True,
        message="Texte extrait avec succès",
        data={
            "job_id": job_id,
            "text": extracted["full_text"],
            "blocks": extracted["blocks"],
            "word_count": len(extracted["full_text"].split()),
            "processing_time_ms": elapsed_ms,
        },
    )
