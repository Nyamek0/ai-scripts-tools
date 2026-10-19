import time
import uuid
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import FileResponse
from typing import Optional

from core.file_handler import file_handler
from core.schemas import JobResponse, JobStatus, APIResponse
from modules.tts.service import synthesize_speech

router = APIRouter()

MODULE_META = {
    "name": "Synthèse vocale (TTS)",
    "description": "Convertit du texte en parole naturelle avec Microsoft Edge TTS (gratuit, multi-voix).",
    "version": "1.0.0",
    "prefix": "/tts",
    "tags": ["tts"],
}

SUPPORTED_VOICES = {
    "fr-FR-DeniseNeural": "Français — Denise (femme)",
    "fr-FR-HenriNeural": "Français — Henri (homme)",
    "en-US-JennyNeural": "English US — Jenny (femme)",
    "en-US-GuyNeural": "English US — Guy (homme)",
    "en-GB-SoniaNeural": "English GB — Sonia (femme)",
    "es-ES-ElviraNeural": "Español — Elvira (femme)",
    "de-DE-KatjaNeural": "Deutsch — Katja (femme)",
    "it-IT-ElsaNeural": "Italiano — Elsa (femme)",
    "pt-BR-FranciscaNeural": "Português BR — Francisca (femme)",
    "ar-SA-ZariyahNeural": "العربية — Zariyah (femme)",
    "zh-CN-XiaoxiaoNeural": "中文 — Xiaoxiao (femme)",
    "ja-JP-NanamiNeural": "日本語 — Nanami (femme)",
}


@router.get("/info", response_model=APIResponse)
async def module_info():
    return APIResponse(
        success=True,
        message="Module info",
        data={
            "name": MODULE_META["name"],
            "description": MODULE_META["description"],
            "max_chars": 5000,
            "output_format": "mp3",
            "voices": SUPPORTED_VOICES,
            "rate_examples": ["-50%", "-20%", "+0%", "+20%", "+50%"],
            "requires_internet": True,
        },
    )


@router.post("/process", response_model=JobResponse)
async def process_text(
    text: str = Form(...),
    voice: Optional[str] = Form(default="fr-FR-DeniseNeural"),
    rate: Optional[str] = Form(default="+0%"),
    volume: Optional[str] = Form(default="+0%"),
):
    """
    Convertit du texte en audio MP3 via Microsoft Edge TTS.

    - text: texte à synthétiser (max 5 000 caractères)
    - voice: identifiant de voix (voir GET /info pour la liste)
    - rate: vitesse de parole (ex: "-20%", "+0%", "+30%")
    - volume: volume (ex: "-10%", "+0%", "+50%")
    """
    text = text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Le texte ne peut pas être vide")
    if len(text) > 5000:
        raise HTTPException(status_code=400, detail="Texte trop long (max 5 000 caractères)")
    if voice not in SUPPORTED_VOICES:
        raise HTTPException(
            status_code=400,
            detail=f"Voix invalide. Voix disponibles: {list(SUPPORTED_VOICES.keys())}",
        )

    start = time.time()
    job_id = str(uuid.uuid4())

    output_path = file_handler.get_output_path(
        job_id=job_id,
        extension=".mp3",
        subfolder="tts",
    )

    try:
        await synthesize_speech(
            text=text,
            output_path=str(output_path),
            voice=voice,
            rate=rate,
            volume=volume,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur synthèse vocale: {str(e)}")

    elapsed_ms = int((time.time() - start) * 1000)

    return JobResponse(
        job_id=job_id,
        status=JobStatus.SUCCESS,
        message="Audio généré avec succès",
        result_url=f"/api/tts/result/{job_id}",
        processing_time_ms=elapsed_ms,
    )


@router.get("/result/{job_id}")
async def get_result(job_id: str):
    import re
    if not re.match(r'^[0-9a-f-]{36}$', job_id):
        raise HTTPException(status_code=400, detail="job_id invalide")

    output_path = file_handler.get_output_path(
        job_id=job_id,
        extension=".mp3",
        subfolder="tts",
    )

    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Résultat introuvable ou expiré")

    return FileResponse(
        path=str(output_path),
        media_type="audio/mpeg",
        filename=f"tts-{job_id}.mp3",
    )
