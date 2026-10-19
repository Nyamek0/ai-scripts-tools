import time
from fastapi import APIRouter, Form, HTTPException
from typing import Optional

from core.schemas import APIResponse
from modules.summarize.service import summarize_text

router = APIRouter()

MODULE_META = {
    "name": "Résumé de texte",
    "description": "Résume automatiquement un texte avec l'algorithme LSA (100% local, sans IA cloud).",
    "version": "1.0.0",
    "prefix": "/summarize",
    "tags": ["summarize"],
}

SUPPORTED_LANGUAGES = {
    "french": "Français",
    "english": "English",
    "spanish": "Español",
    "german": "Deutsch",
    "italian": "Italiano",
    "portuguese": "Português",
    "arabic": "العربية",
    "chinese": "中文",
}


@router.get("/info", response_model=APIResponse)
async def module_info():
    return APIResponse(
        success=True,
        message="Module info",
        data={
            "name": MODULE_META["name"],
            "description": MODULE_META["description"],
            "max_chars": 50000,
            "supported_languages": SUPPORTED_LANGUAGES,
            "sentences_range": "1–20",
            "algorithm": "LSA (Latent Semantic Analysis) via sumy",
            "requires_internet": False,
        },
    )


@router.post("/process", response_model=APIResponse)
async def process_text(
    text: str = Form(...),
    language: Optional[str] = Form(default="french"),
    sentences: Optional[int] = Form(default=5),
):
    """
    Résume un texte avec LSA.

    - text: texte à résumer (max 50 000 caractères)
    - language: langue du texte (french, english, spanish, german, italian, portuguese)
    - sentences: nombre de phrases dans le résumé (1–20)
    """
    text = text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Le texte ne peut pas être vide")
    if len(text) > 50000:
        raise HTTPException(status_code=400, detail="Texte trop long (max 50 000 caractères)")
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Langue non supportée: {language}. Langues disponibles: {list(SUPPORTED_LANGUAGES.keys())}",
        )
    if not 1 <= sentences <= 20:
        raise HTTPException(status_code=400, detail="sentences doit être entre 1 et 20")

    start = time.time()

    try:
        result = summarize_text(
            text=text,
            language=language,
            sentences_count=sentences,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur résumé: {str(e)}")

    elapsed_ms = int((time.time() - start) * 1000)

    return APIResponse(
        success=True,
        message="Résumé généré avec succès",
        data={
            "summary": result["summary"],
            "original_chars": len(text),
            "summary_chars": len(result["summary"]),
            "compression_ratio": round(len(result["summary"]) / len(text), 3),
            "sentences_count": result["sentences_count"],
            "language": language,
            "processing_time_ms": elapsed_ms,
        },
    )
