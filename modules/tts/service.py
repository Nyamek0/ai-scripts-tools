import logging
from pathlib import Path

logger = logging.getLogger(__name__)


async def synthesize_speech(
    text: str,
    output_path: str,
    voice: str = "fr-FR-DeniseNeural",
    rate: str = "+0%",
    volume: str = "+0%",
) -> None:
    """
    Synthétise du texte en audio MP3 via Microsoft Edge TTS.

    Installation: pip install edge-tts
    Requiert une connexion internet (API Microsoft, gratuite, sans clé API).

    Args:
        text: Texte à synthétiser
        output_path: Chemin de sortie MP3
        voice: Identifiant de voix Edge TTS (ex: "fr-FR-DeniseNeural")
        rate: Vitesse de parole (ex: "+0%", "-20%", "+30%")
        volume: Volume (ex: "+0%", "+50%")
    """
    try:
        import edge_tts
    except ImportError:
        raise RuntimeError("Installez edge-tts: pip install edge-tts")

    logger.info(f"🎙️  TTS: voix={voice}, {len(text)} caractères")

    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
    await communicate.save(output_path)

    size = Path(output_path).stat().st_size
    logger.info(f"✅ Audio généré: {output_path} ({size} bytes)")
