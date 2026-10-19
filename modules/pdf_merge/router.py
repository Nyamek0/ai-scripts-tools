import time
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List

from core.file_handler import file_handler
from core.schemas import JobResponse, JobStatus, APIResponse
from core.config import settings
from modules.pdf_merge.service import merge_pdfs

router = APIRouter()

MODULE_META = {
    "name": "Fusion PDF",
    "description": "Fusionne plusieurs fichiers PDF en un seul document (pypdf, 100% local).",
    "version": "1.0.0",
    "prefix": "/pdf-merge",
    "tags": ["pdf-merge"],
}


@router.get("/info", response_model=APIResponse)
async def module_info():
    return APIResponse(
        success=True,
        message="Module info",
        data={
            "name": MODULE_META["name"],
            "description": MODULE_META["description"],
            "accepted_types": settings.ALLOWED_PDF_TYPES,
            "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
            "max_files": 20,
        },
    )


@router.post("/process", response_model=JobResponse)
async def process_pdfs(
    files: List[UploadFile] = File(...),
):
    """
    Upload plusieurs fichiers PDF → retourne le PDF fusionné.
    Ordre de fusion = ordre d'upload.
    Minimum 2 fichiers, maximum 20.
    """
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Minimum 2 fichiers PDF requis")
    if len(files) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 fichiers PDF")

    start = time.time()

    saved_paths = []
    job_id = None

    for i, file in enumerate(files):
        upload_meta = await file_handler.save_upload(
            file=file,
            allowed_types=settings.ALLOWED_PDF_TYPES,
            subfolder="pdf_merge",
        )
        if i == 0:
            job_id = upload_meta["job_id"]
        saved_paths.append(upload_meta["saved_path"])

    output_path = file_handler.get_output_path(
        job_id=job_id,
        extension=".pdf",
        subfolder="pdf_merge",
    )

    try:
        result = merge_pdfs(
            input_paths=saved_paths,
            output_path=str(output_path),
        )
    except Exception as e:
        file_handler.cleanup_job(job_id, subfolder="pdf_merge")
        raise HTTPException(status_code=500, detail=f"Erreur fusion PDF: {str(e)}")
    finally:
        for path in saved_paths:
            try:
                Path(path).unlink(missing_ok=True)
            except Exception:
                pass

    elapsed_ms = int((time.time() - start) * 1000)

    return JobResponse(
        job_id=job_id,
        status=JobStatus.SUCCESS,
        message=f"PDF fusionné avec succès ({result['page_count']} pages)",
        result_url=f"/api/pdf-merge/result/{job_id}",
        processing_time_ms=elapsed_ms,
    )


@router.get("/result/{job_id}")
async def get_result(job_id: str):
    import re
    if not re.match(r'^[0-9a-f-]{36}$', job_id):
        raise HTTPException(status_code=400, detail="job_id invalide")

    output_path = file_handler.get_output_path(
        job_id=job_id,
        extension=".pdf",
        subfolder="pdf_merge",
    )

    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Résultat introuvable ou expiré")

    return FileResponse(
        path=str(output_path),
        media_type="application/pdf",
        filename=f"merged-{job_id}.pdf",
    )
