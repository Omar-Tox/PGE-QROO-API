import hashlib
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.config import settings
from app.db.connection import get_session
from app.db.models import PersonalAccessToken, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.LARAVEL_LOGIN_URL)

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_session)
) -> User:
    # 1. Validar formato
    if "|" not in token:
        raw_token = token
    else:
        try:
            _, raw_token = token.split("|", 1)
        except ValueError:
             raise HTTPException(status_code=401, detail="Token inválido")

    # 2. Hashear
    hashed_token = hashlib.sha256(raw_token.encode()).hexdigest()

    # 3. Buscar token
    stmt = select(PersonalAccessToken).where(PersonalAccessToken.token == hashed_token)
    access_token = db.execute(stmt).scalar_one_or_none()

    if not access_token:
        raise HTTPException(status_code=401, detail="Token expirado o inválido")

    # 4. Buscar usuario (Tabla 'usuarios', PK 'id_usuario')
    # IMPORTANTE: SQLAlchemy usa 'joinedload' por defecto para relaciones simples, 
    # pero para la validación de permisos necesitamos cargar las dependencias.
    # Lo haremos en el paso de validación de permisos para no hacer pesada esta función.
    
    user_stmt = select(User).where(User.id_usuario == access_token.tokenable_id)
    user = db.execute(user_stmt).scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    if not user.activo:
         raise HTTPException(status_code=401, detail="Usuario inactivo")

    return user