import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    String, Boolean, Integer, BigInteger, DateTime, Text, ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class Job(Base):
    """
    Trace chaque traitement soumis à la plateforme.
    Un job = un appel à /api/<module>/process.
    """
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    # Lien vers l'utilisateur (nullable = jobs anonymes avant auth)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    # Quel module a été utilisé (ex: "bg_remove", "ocr", "tts")
    module_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Statut du job
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True,
    )  # pending | processing | success | failed

    # Fichier d'entrée
    input_filename: Mapped[str | None] = mapped_column(String(500), nullable=True)
    input_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    # Résultat
    result_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    output_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    # Erreur (si failed)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Performances
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    def __repr__(self) -> str:
        return f"<Job id={self.id} module={self.module_name} status={self.status}>"


class ModuleStat(Base):
    """
    Compteurs d'utilisation agrégés par module.
    Une ligne par module — mise à jour à chaque job terminé.
    """
    __tablename__ = "module_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    module_name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True,
    )
    total_jobs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    successful_jobs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_jobs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_processing_time_ms: Mapped[int] = mapped_column(
        BigInteger, default=0, nullable=False,
    )
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    def __repr__(self) -> str:
        return f"<ModuleStat module={self.module_name} total={self.total_jobs}>"
