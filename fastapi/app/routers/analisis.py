# ============================================================
#  app/routers/analisis.py
#  Endpoints reales para análisis energético
#  CORREGIDO: Apunta a la dependencia SÍNCRONA (get_session)
# ============================================================

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.connection import get_session
from app.services import analisis_service as service
from app.core.security import get_current_user # <--- Importar seguridad
from app.db.models import User

router = APIRouter(
    prefix="/analisis",
    tags=["Análisis Energético (Privado)"]
)

# ============================================================
# NOTA DE SEGURIDAD:
# Todos los endpoints ahora requieren un token válido de Laravel.
# El usuario se inyecta en 'current_user'.
# ============================================================

@router.get("/consumo-total-anual/{id_edificio}")
def consumo_total_anual(
    id_edificio: int, 
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user) # 🔒 Candado
):
    return service.consumo_total_anual(db, id_edificio)


@router.get("/consumo-mensual/{id_edificio}/{anio}")
def consumo_mensual(
    id_edificio: int, 
    anio: int, 
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user) # 🔒 Candado
):
    return service.consumo_mensual(db, id_edificio, anio)


@router.get("/costo-anual/{id_edificio}")
def costo_total_anual(
    id_edificio: int, 
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user) # 🔒 Candado
):
    return service.costo_total_anual(db, id_edificio)


@router.get("/consumo-promedio-anual/{id_edificio}")
def consumo_promedio_anual(
    id_edificio: int, 
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user) # 🔒 Candado
):
    return service.consumo_promedio_anual(db, id_edificio)


@router.get("/estacionalidad/{id_edificio}")
def estacionalidad(
    id_edificio: int, 
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user) # 🔒 Candado
):
    return service.estacionalidad(db, id_edificio)


@router.get("/ranking/{id_edificio}")
def ranking_consumo(
    id_edificio: int,
    top: int = Query(5, ge=1, le=50),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user) # 🔒 Candado
):
    return service.ranking_meses(db, id_edificio, top)


@router.get("/tendencia/{id_edificio}")
def tendencia(
    id_edificio: int,
    window: int = Query(3, ge=1, le=12),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user) # 🔒 Candado
):
    return service.tendencia(db, id_edificio, window)


@router.get("/anio-mayor-consumo/{id_edificio}")
def anio_mayor_consumo(
    id_edificio: int, 
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user) # 🔒 Candado
):
    return service.anio_mayor_consumo(db, id_edificio)


@router.get("/ahorro-potencial/{id_edificio}")
def ahorro_potencial(
    id_edificio: int, 
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user) # 🔒 Candado
):
    return service.potencial_ahorro(db, id_edificio)