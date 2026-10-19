from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import decode_access_token
from modules.auth.models import User
from modules.auth.service import get_user_by_id

bearer_scheme = HTTPBearer(auto_error=False)

_UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token invalide ou expiré",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dépendance FastAPI — extrait et valide le token Bearer, retourne l'utilisateur.

    Usage dans un endpoint protégé :
        @router.get("/protected")
        async def protected(user: User = Depends(get_current_user)):
            ...
    """
    if credentials is None:
        raise _UNAUTHORIZED

    try:
        payload = decode_access_token(credentials.credentials)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise _UNAUTHORIZED
    except JWTError:
        raise _UNAUTHORIZED

    user = await get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise _UNAUTHORIZED

    return user


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """
    Variante optionnelle — retourne None si pas de token (endpoints semi-publics).
    """
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
