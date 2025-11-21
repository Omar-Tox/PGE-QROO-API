import hashlib
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional

from app.db.connection import get_session
from app.db.models import PersonalAccessToken, User

# Esquema OAuth2 (Le dice a Swagger UI que pida un token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") # La URL es simbólica aquí

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_session)
) -> User:
    """
    Valida el token de Sanctum y devuelve el usuario actual.
    """
    # 1. Sanctum espera el token en formato "id|token_plano"
    if "|" not in token:
        # A veces el cliente envía solo el token plano, intentamos manejarlo
        raw_token = token
    else:
        # Extraemos la parte del hash (lo que está después del |)
        try:
            tokenId, raw_token = token.split("|", 1)
        except ValueError:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Formato de token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # 2. Hashear el token (SHA-256) para compararlo con la DB
    hashed_token = hashlib.sha256(raw_token.encode()).hexdigest()

    # 3. Buscar en la base de datos
    stmt = select(PersonalAccessToken).where(PersonalAccessToken.token == hashed_token)
    access_token = db.execute(stmt).scalar_one_or_none()

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. Buscar el usuario asociado
    # Asumimos que tokenable_type es 'App\Models\User'
    user_stmt = select(User).where(User.id == access_token.tokenable_id)
    user = db.execute(user_stmt).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )

    return user