from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase

from core.config import settings


def _async_url(url: str) -> str:
    """Convertit une URL postgresql:// en postgresql+asyncpg://."""
    return url.replace("postgresql://", "postgresql+asyncpg://", 1)


engine = create_async_engine(
    _async_url(settings.DATABASE_URL),
    echo=settings.DEBUG,       # SQL logs en mode DEBUG
    pool_pre_ping=True,        # Vérifie les connexions avant usage
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Classe de base pour tous les modèles SQLAlchemy."""
    pass


async def create_all_tables() -> None:
    """Crée toutes les tables en base (appelé au démarrage de l'app)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """
    Dépendance FastAPI — fournit une session DB par requête.

    Usage:
        @router.get("/")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
