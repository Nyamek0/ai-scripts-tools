import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_text(input_path: str, languages: list[str] = None) -> dict:
    """
    Extrait le texte d'une image via EasyOCR.

    Installation: pip install easyocr
    Les modèles sont téléchargés automatiquement au premier appel.

    Args:
        input_path: Chemin vers l'image
        languages: Liste de codes ISO (ex: ['fr', 'en'])

    Returns:
        dict { full_text: str, blocks: list[dict] }
    """
    try:
        import easyocr
    except ImportError:
        raise RuntimeError("Installez easyocr: pip install easyocr")

    if not languages:
        languages = ["fr", "en"]

    logger.info(f"📖 OCR: {input_path} (langues={languages})")

    reader = easyocr.Reader(languages, gpu=False)
    results = reader.readtext(input_path)

    blocks = []
    lines = []

    for (bbox, text, confidence) in results:
        if confidence > 0.3:  # Filtrer les résultats peu fiables
            blocks.append({
                "text": text,
                "confidence": round(confidence, 3),
                "bbox": bbox,
            })
            lines.append(text)

    full_text = "\n".join(lines)

    logger.info(f"✅ OCR terminé: {len(blocks)} blocs, {len(full_text)} caractères")

    return {
        "full_text": full_text,
        "blocks": blocks,
    }
