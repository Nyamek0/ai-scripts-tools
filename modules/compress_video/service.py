import logging
import subprocess
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

QUALITY_PRESETS = {
    "high":   {"crf": 20, "preset": "slow"},
    "medium": {"crf": 28, "preset": "medium"},
    "low":    {"crf": 35, "preset": "fast"},
}


def compress_video(
    input_path: str,
    output_path: str,
    quality: str = "medium",
) -> dict:
    """
    Compresse une vidéo avec ffmpeg (H.264 + AAC).

    Requiert: ffmpeg installé sur le système
        apt install ffmpeg  (Ubuntu/Debian)
        brew install ffmpeg (macOS)

    Args:
        input_path: Chemin de la vidéo source
        output_path: Chemin de la vidéo compressée (.mp4)
        quality: high | medium | low

    Returns:
        dict { input_size_bytes, output_size_bytes }
    """
    if not shutil.which("ffmpeg"):
        raise RuntimeError(
            "ffmpeg n'est pas installé. "
            "Installez-le: apt install ffmpeg  (ou brew install ffmpeg sur macOS)"
        )

    preset = QUALITY_PRESETS.get(quality, QUALITY_PRESETS["medium"])
    input_size = Path(input_path).stat().st_size

    logger.info(
        f"🎬 Compression vidéo: {input_path} "
        f"({input_size // 1024}KB) qualité={quality} "
        f"CRF={preset['crf']}"
    )

    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-c:v", "libx264",
        "-crf", str(preset["crf"]),
        "-preset", preset["preset"],
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",  # Optimisation lecture web
        "-y",
        output_path,
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300,  # 5 minutes max
    )

    if result.returncode != 0:
        logger.error(f"Erreur ffmpeg stderr: {result.stderr[-1000:]}")
        raise RuntimeError(f"ffmpeg a échoué (code {result.returncode}): {result.stderr[-300:]}")

    output_size = Path(output_path).stat().st_size
    logger.info(
        f"✅ Vidéo compressée: {output_size // 1024}KB "
        f"(réduction: {round((1 - output_size / input_size) * 100, 1)}%) → {output_path}"
    )

    return {
        "input_size_bytes": input_size,
        "output_size_bytes": output_size,
    }
