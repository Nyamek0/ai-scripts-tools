from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import create_access_token
from core.schemas import APIResponse
from modules.auth.schemas import UserRegister, UserLogin, TokenResponse, UserOut
from modules.auth.service import create_user, authenticate_user
from modules.auth.dependencies import get_current_user
from modules.auth.models import User

router = APIRouter()

MODULE_META = {
    "name": "Authentification JWT",
    "description": "Inscription, connexion et profil utilisateur avec tokens JWT (Se souvenir de moi inclus).",
    "version": "1.0.0",
    "prefix": "/auth",
    "tags": ["auth"],
}


@router.post(
    "/register",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un compte",
)
async def register(
    body: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """
    Crée un nouveau compte utilisateur.

    - **email**: adresse email unique
    - **password**: min 8 caractères, doit contenir lettres + chiffres
    - **full_name**: optionnel
    """
    try:
        user = await create_user(
            db=db,
            email=body.email,
            password=body.password,
            full_name=body.full_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return APIResponse(
        success=True,
        message="Compte créé avec succès",
        data=UserOut.model_validate(user).model_dump(),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Se connecter",
)
async def login(
    body: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """
    Authentifie l'utilisateur et retourne un token JWT.

    - **remember_me**: `false` → token valide 1 heure | `true` → token valide 30 jours
    """
    user = await authenticate_user(db=db, email=body.email, password=body.password)

    if not user:
        # Même message pour email introuvable et mauvais mdp (sécurité)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token, expires_at = create_access_token(
        subject=str(user.id),
        remember_me=body.remember_me,
    )

    return TokenResponse(
        access_token=token,
        expires_at=expires_at,
        remember_me=body.remember_me,
        user=UserOut.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserOut,
    summary="Profil de l'utilisateur connecté",
)
async def me(current_user: User = Depends(get_current_user)):
    """
    Retourne le profil de l'utilisateur authentifié.
    Requiert le header : `Authorization: Bearer <token>`
    """
    return UserOut.model_validate(current_user)
