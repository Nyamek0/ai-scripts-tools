import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def convert_image_format(
    input_path: str,
    output_path: str,
    output_format: str = "jpeg",
    quality: int = 85,
    resize_width: int = None,
    resize_height: int = None,
) -> dict:
    """
    Convertit une image dans un autre format avec Pillow.

    Args:
        input_path: Chemin de l'image source
        output_path: Chemin de l'image de sortie
        output_format: Format cible (jpeg, png, webp, bmp, gif, tiff)
        quality: Qualité 1–100 (JPEG/WebP uniquement)
        resize_width: Largeur cible en px (None = conserver)
        resize_height: Hauteur cible en px (None = conserver)

    Returns:
        dict { width, height, format, file_size_bytes }
    """
    try:
        from PIL import Image
    except ImportError:
        raise RuntimeError("Installez Pillow: pip install Pillow")

    logger.info(f"🖼️  Conversion: {input_path} → {output_format.upper()}")

    with Image.open(input_path) as img:
        # JPEG ne supporte pas la transparence → convertir en RGB avec fond blanc
        if output_format == "jpeg" and img.mode in ("RGBA", "P", "LA"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            src = img.convert("RGBA") if img.mode == "P" else img
            background.paste(src, mask=src.split()[-1])
            img = background
        elif output_format == "jpeg" and img.mode != "RGB":
            img = img.convert("RGB")

        # Redimensionnement en conservant les proportions si une seule dimension est donnée
        if resize_width or resize_height:
            orig_w, orig_h = img.size
            if resize_width and resize_height:
                new_size = (resize_width, resize_height)
            elif resize_width:
                new_size = (resize_width, max(1, int(orig_h * resize_width / orig_w)))
            else:
                new_size = (max(1, int(orig_w * resize_height / orig_h)), resize_height)
            img = img.resize(new_size, Image.LANCZOS)
            logger.info(f"  Redimensionné: {orig_w}×{orig_h} → {new_size[0]}×{new_size[1]}")

        final_w, final_h = img.size

        save_kwargs = {}
        if output_format in ("jpeg", "webp"):
            save_kwargs["quality"] = quality
            save_kwargs["optimize"] = True
        elif output_format == "png":
            save_kwargs["optimize"] = True

        pil_format = "JPEG" if output_format == "jpeg" else output_format.upper()
        img.save(output_path, format=pil_format, **save_kwargs)

    file_size = Path(output_path).stat().st_size
    logger.info(f"✅ Image convertie: {final_w}×{final_h}px {file_size}B → {output_path}")

    return {
        "width": final_w,
        "height": final_h,
        "format": output_format,
        "file_size_bytes": file_size,
    }
