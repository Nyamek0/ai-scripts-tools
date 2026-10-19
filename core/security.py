from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from core.config import settings

# ── Hashing des mots de passe ─────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ── Tokens JWT ────────────────────────────────────────────────────────────────

def create_access_token(
    subject: str,
    remember_me: bool = False,
    extra_claims: Optional[dict] = None,
) -> tuple[str, datetime]:
    """
    Génère un token JWT signé.

    Args:
        subject:     Identifiant unique de l'utilisateur (email ou user_id)
        remember_me: Si True → expire dans 30 jours, sinon 1 heure
        extra_claims: Claims additionnels à inclure dans le payload (optionnel)

    Returns:
        (token: str, expires_at: datetime)
    """
    if remember_me:
        delta = timedelta(days=settings.ACCESS_TOKEN_REMEMBER_ME_DAYS)
    else:
        delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    expires_at = datetime.now(timezone.utc) + delta

    payload = {
        "sub": str(subject),
        "exp": expires_at,
        "iat": datetime.now(timezone.utc),
        "remember_me": remember_me,
    }
    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, expires_at


def decode_access_token(token: str) -> dict:
    """
    Décode et valide un token JWT.

    Returns:
        Le payload décodé.

    Raises:
        JWTError si le token est invalide, expiré ou malformé.
    """
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
