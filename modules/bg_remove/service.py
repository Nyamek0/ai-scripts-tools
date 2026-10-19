from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def remove_background(input_path: str, output_path: str) -> None:
    """
    Supprime le fond d'une image en utilisant rembg.
    
    Installation: pip install rembg[gpu] onnxruntime
    Le modèle u2net est téléchargé automatiquement au premier appel (~170MB).
    
    Args:
        input_path: Chemin vers l'image source
        output_path: Chemin de sortie (PNG avec transparence)
    """
    try:
        from rembg import remove
        from PIL import Image
    except ImportError:
        raise RuntimeError(
            "Dépendances manquantes. Installez: pip install rembg pillow"
        )

    logger.info(f"🎨 Suppression de fond: {input_path} → {output_path}")

    input_image = Image.open(input_path)

    # rembg gère automatiquement la transparence → PNG
    output_image = remove(input_image)

    # S'assurer que la sortie est bien en RGBA (transparence)
    if output_image.mode != "RGBA":
        output_image = output_image.convert("RGBA")

    output_image.save(output_path, "PNG")

    logger.info(f"✅ Fond supprimé → {output_path}")
