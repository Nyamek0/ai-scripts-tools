import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def merge_pdfs(input_paths: list[str], output_path: str) -> dict:
    """
    Fusionne plusieurs PDFs en un seul fichier.

    Installation: pip install pypdf

    Args:
        input_paths: Liste des chemins PDF à fusionner (dans l'ordre)
        output_path: Chemin du PDF de sortie

    Returns:
        dict { page_count: int, file_size_bytes: int }
    """
    try:
        from pypdf import PdfWriter, PdfReader
    except ImportError:
        raise RuntimeError("Installez pypdf: pip install pypdf")

    writer = PdfWriter()
    total_pages = 0

    for path in input_paths:
        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)
            total_pages += 1
        logger.info(f"📄 Ajouté: {path} ({len(reader.pages)} pages)")

    with open(output_path, "wb") as f:
        writer.write(f)

    file_size = Path(output_path).stat().st_size
    logger.info(f"✅ PDF fusionné: {total_pages} pages → {output_path}")

    return {
        "page_count": total_pages,
        "file_size_bytes": file_size,
    }
