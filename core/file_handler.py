import uuid
import shutil
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta
from fastapi import UploadFile, HTTPException

from core.config import settings

logger = logging.getLogger(__name__)


class FileHandler:
    """
    Gestionnaire de fichiers unifié pour tous les modules.
    Gère : upload, validation, sauvegarde, nettoyage automatique.
    """

    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.output_dir = Path(settings.OUTPUT_DIR)
        self.upload_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

    def _generate_job_id(self) -> str:
        return str(uuid.uuid4())

    def _validate_size(self, file: UploadFile):
        max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        # FastAPI ne donne pas la taille directement — on vérifie après sauvegarde

    def _validate_type(self, file: UploadFile, allowed_types: list[str]):
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=415,
                detail=f"Type de fichier non supporté: {file.content_type}. "
                       f"Types acceptés: {', '.join(allowed_types)}",
            )

    async def save_upload(
        self,
        file: UploadFile,
        allowed_types: list[str],
        subfolder: str = "",
    ) -> dict:
        """
        Sauvegarde un fichier uploadé et retourne ses métadonnées.
        Retourne: { job_id, original_name, saved_path, content_type, size_bytes }
        """
        self._validate_type(file, allowed_types)

        job_id = self._generate_job_id()
        ext = Path(file.filename).suffix.lower()
        save_dir = self.upload_dir / subfolder if subfolder else self.upload_dir
        save_dir.mkdir(parents=True, exist_ok=True)

        save_path = save_dir / f"{job_id}{ext}"

        try:
            content = await file.read()
            size_bytes = len(content)

            if size_bytes > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
                raise HTTPException(
                    status_code=413,
                    detail=f"Fichier trop volumineux. Maximum: {settings.MAX_FILE_SIZE_MB}MB",
                )

            save_path.write_bytes(content)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erreur sauvegarde fichier: {e}")
            raise HTTPException(status_code=500, detail="Erreur lors de la sauvegarde du fichier")

        logger.info(f"📁 Fichier sauvegardé: {save_path} ({size_bytes} bytes)")

        return {
            "job_id": job_id,
            "original_name": file.filename,
            "saved_path": str(save_path),
            "content_type": file.content_type,
            "size_bytes": size_bytes,
        }

    def get_output_path(self, job_id: str, extension: str, subfolder: str = "") -> Path:
        """Retourne le chemin de sortie pour un job donné."""
        out_dir = self.output_dir / subfolder if subfolder else self.output_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir / f"{job_id}{extension}"

    def cleanup_job(self, job_id: str, subfolder: str = ""):
        """Supprime les fichiers temporaires d'un job."""
        for base_dir in [self.upload_dir, self.output_dir]:
            target = base_dir / subfolder if subfolder else base_dir
            for f in target.glob(f"{job_id}*"):
                try:
                    f.unlink()
                    logger.info(f"🗑️  Supprimé: {f}")
                except Exception as e:
                    logger.warning(f"Impossible de supprimer {f}: {e}")

    def cleanup_old_files(self, max_age_hours: int = 24):
        """Nettoie les fichiers plus vieux que max_age_hours."""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        count = 0
        for base_dir in [self.upload_dir, self.output_dir]:
            for f in base_dir.rglob("*"):
                if f.is_file():
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    if mtime < cutoff:
                        try:
                            f.unlink()
                            count += 1
                        except Exception:
                            pass
        logger.info(f"🧹 Nettoyage: {count} fichier(s) supprimé(s)")
        return count


# Singleton partagé par tous les modules
file_handler = FileHandler()
