import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import hash_password, verify_password
from modules.auth.models import User

logger = logging.getLogger(__name__)


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email.lower()))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    email: str,
    password: str,
    full_name: Optional[str] = None,
    is_superadmin: bool = False,
) -> User:
    """
    Crée un nouvel utilisateur en base.

    Raises:
        ValueError si l'email est déjà utilisé.
    """
    existing = await get_user_by_email(db, email)
    if existing:
        raise ValueError(f"Un compte existe déjà avec l'email: {email}")

    user = User(
        email=email.lower().strip(),
        hashed_password=hash_password(password),
        full_name=full_name,
        is_superadmin=is_superadmin,
        is_verified=is_superadmin,  # le superadmin est vérifié d'office
    )
    db.add(user)
    await db.flush()   # récupère l'id sans commit (le commit est fait par get_db)
    await db.refresh(user)

    logger.info(f"✅ Nouvel utilisateur créé: {user.email} (id={user.id})")
    return user


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> Optional[User]:
    """
    Vérifie email + mot de passe.

    Returns:
        L'utilisateur si les identifiants sont valides, None sinon.
    """
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user
