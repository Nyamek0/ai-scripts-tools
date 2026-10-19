import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def transcribe_audio(
    input_path: str,
    output_path: str,
    language: str | None = None,
    model_name: str = "base",
    output_format: str = "txt",
) -> dict:
    """
    Transcrit un fichier audio en texte via OpenAI Whisper (local).

    Installation: pip install openai-whisper
    Modèles disponibles: tiny, base, small, medium, large
    Le modèle est téléchargé automatiquement au premier appel.

    Args:
        input_path: Chemin audio source
        output_path: Chemin de sortie
        language: Code ISO (None = auto-détection)
        model_name: Taille du modèle Whisper
        output_format: "txt" | "srt" | "json"

    Returns:
        dict avec le texte transcrit et les segments
    """
    try:
        import whisper
    except ImportError:
        raise RuntimeError("Installez whisper: pip install openai-whisper")

    logger.info(f"🎙️  Transcription: {input_path} (modèle={model_name}, langue={language or 'auto'})")

    model = whisper.load_model(model_name)

    result = model.transcribe(
        input_path,
        language=language,
        verbose=False,
    )

    # Écriture du résultat selon le format demandé
    if output_format == "txt":
        Path(output_path).write_text(result["text"].strip(), encoding="utf-8")

    elif output_format == "srt":
        srt_content = _segments_to_srt(result["segments"])
        Path(output_path).write_text(srt_content, encoding="utf-8")

    elif output_format == "json":
        output_data = {
            "text": result["text"].strip(),
            "language": result.get("language", "unknown"),
            "segments": [
                {
                    "id": s["id"],
                    "start": round(s["start"], 3),
                    "end": round(s["end"], 3),
                    "text": s["text"].strip(),
                }
                for s in result["segments"]
            ],
        }
        Path(output_path).write_text(
            json.dumps(output_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    logger.info(f"✅ Transcription terminée → {output_path}")
    return result


def _segments_to_srt(segments: list) -> str:
    """Convertit les segments Whisper en format SRT."""
    lines = []
    for i, seg in enumerate(segments, start=1):
        start = _format_srt_time(seg["start"])
        end = _format_srt_time(seg["end"])
        lines.append(f"{i}\n{start} --> {end}\n{seg['text'].strip()}\n")
    return "\n".join(lines)


def _format_srt_time(seconds: float) -> str:
    """Formate un temps en secondes vers HH:MM:SS,mmm (format SRT)."""
    ms = int((seconds % 1) * 1000)
    s = int(seconds) % 60
    m = int(seconds // 60) % 60
    h = int(seconds // 3600)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
