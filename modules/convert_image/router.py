import time
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from typing import Optional

from core.file_handler import file_handler
from core.schemas import JobResponse, JobStatus, APIResponse
from core.config import settings
from modules.convert_image.service import convert_image_format

router = APIRouter()

MODULE_META = {
    "name": "Conversion d'image",
    "description": "Convertit une image dans un autre format (JPEG, PNG, WebP, BMP, GIF, TIFF) avec Pillow.",
    "version": "1.0.0",
    "prefix": "/convert-image",
    "tags": ["convert-image"],
}

OUTPUT_FORMATS = {
    "jpeg": {"ext": ".jpg",  "mime": "image/jpeg"},
    "png":  {"ext": ".png",  "mime": "image/png"},
    "webp": {"ext": ".webp", "mime": "image/webp"},
    "bmp":  {"ext": ".bmp",  "mime": "image/bmp"},
    "gif":  {"ext": ".gif",  "mime": "image/gif"},
    "tiff": {"ext": ".tiff", "mime": "image/tiff"},
}


@router.get("/info", response_model=APIResponse)
async def module_info():
    return APIResponse(
        success=True,
        message="Module info",
        data={
            "name": MODULE_META["name"],
            "description": MODULE_META["description"],
            "accepted_input_types": settings.ALLOWED_IMAGE_TYPES,
            "supported_output_formats": list(OUTPUT_FORMATS.keys()),
            "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
            "quality_note": "quality (1-100) s'applique uniquement à JPEG et WebP",
        },
    )


@router.post("/process", response_model=JobResponse)
async def process_image(
    file: UploadFile = File(...),
    output_format: str = Form(...),
    quality: Optional[int] = Form(default=85),
    resize_width: Optional[int] = Form(default=None),
    resize_height: Optional[int] = Form(default=None),
):
    """
    Convertit une image vers un autre format.

    - output_format: jpeg | png | webp | bmp | gif | tiff
    - quality: compression 1–100 (JPEG et WebP uniquement, défaut: 85)
    - resize_width: largeur cible en px (optionnel)
    - resize_height: hauteur cible en px (optionnel)
      → Si un seul dimension est fourni, les proportions sont conservées.
    """
    output_format = output_format.lower().strip()
    if output_format not in OUTPUT_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Format invalide. Formats supportés: {list(OUTPUT_FORMATS.keys())}",
        )
    if not 1 <= quality <= 100:
        raise HTTPException(status_code=400, detail="quality doit être entre 1 et 100")

    start = time.time()

    upload_meta = await file_handler.save_upload(
        file=file,
        allowed_types=settings.ALLOWED_IMAGE_TYPES,
        subfolder="convert_image",
    )

    job_id = upload_meta["job_id"]
    fmt_info = OUTPUT_FORMATS[output_format]
    output_path = file_handler.get_output_path(
        job_id=job_id,
        extension=fmt_info["ext"],
        subfolder="convert_image",
    )

    try:
        result = convert_image_format(
            input_path=upload_meta["saved_path"],
            output_path=str(output_path),
            output_format=output_format,
            quality=quality,
            resize_width=resize_width,
            resize_height=resize_height,
        )
    except Exception as e:
        file_handler.cleanup_job(job_id, subfolder="convert_image")
        raise HTTPException(status_code=500, detail=f"Erreur conversion: {str(e)}")
    finally:
        try:
            Path(upload_meta["saved_path"]).unlink(missing_ok=True)
        except Exception:
            pass

    elapsed_ms = int((time.time() - start) * 1000)

    return JobResponse(
        job_id=job_id,
        status=JobStatus.SUCCESS,
        message=f"Image convertie en {output_format.upper()} ({result['width']}×{result['height']}px)",
        result_url=f"/api/convert-image/result/{job_id}?format={output_format}",
        processing_time_ms=elapsed_ms,
    )


@router.get("/result/{job_id}")
async def get_result(job_id: str, format: str = "jpeg"):
    import re
    if not re.match(r'^[0-9a-f-]{36}$', job_id):
        raise HTTPException(status_code=400, detail="job_id invalide")

    format = format.lower()
    if format not in OUTPUT_FORMATS:
        raise HTTPException(status_code=400, detail=f"Format invalide. Options: {list(OUTPUT_FORMATS.keys())}")

    fmt_info = OUTPUT_FORMATS[format]
    output_path = file_handler.get_output_path(
        job_id=job_id,
        extension=fmt_info["ext"],
        subfolder="convert_image",
    )

    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Résultat introuvable ou expiré")

    return FileResponse(
        path=str(output_path),
        media_type=fmt_info["mime"],
        filename=f"converted-{job_id}{fmt_info['ext']}",
    )
