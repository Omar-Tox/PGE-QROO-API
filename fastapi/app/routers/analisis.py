# ============================================================
#  app/routers/analisis.py
#  Endpoints reales para análisis energético
#  CORREGIDO: Apunta a la dependencia SÍNCRONA (get_session)
# ============================================================

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session


from app.db.connection import get_session

from app.services import analisis_service as service

router = APIRouter(
    prefix="/analisis",
    tags=["Análisis Energético"]
)


# ------------------------------------------------------------
# 1) Consumo total anual
# ------------------------------------------------------------
@router.get("/consumo-total-anual/{id_edificio}")
def consumo_total_anual(id_edificio: int, db: Session = Depends(get_session)):
    return service.consumo_total_anual(db, id_edificio)


# ------------------------------------------------------------
# 2) Consumo mensual (por año)
# ------------------------------------------------------------
@router.get("/consumo-mensual/{id_edificio}/{anio}")
def consumo_mensual(id_edificio: int, anio: int, db: Session = Depends(get_session)):
    """
    Regresa los consumos por mes para un año.
    """
    return service.consumo_mensual(db, id_edificio, anio)


# ------------------------------------------------------------
# 3) Costo total anual
# ------------------------------------------------------------
@router.get("/costo-anual/{id_edificio}")
def costo_total_anual(id_edificio: int, db: Session = Depends(get_session)):
    """
    Regresa el costo total por año.
    """
    return service.costo_total_anual(db, id_edificio)


# ------------------------------------------------------------
# 4) Consumo promedio anual
# ------------------------------------------------------------
@router.get("/consumo-promedio-anual/{id_edificio}")
def consumo_promedio_anual(id_edificio: int, db: Session = Depends(get_session)):
    """
    Regresa el promedio kWh por año.
    """
    return service.consumo_promedio_anual(db, id_edificio)


# ------------------------------------------------------------
# 5) Estacionalidad (promedio por mes)
# ------------------------------------------------------------
@router.get("/estacionalidad/{id_edificio}")
def estacionalidad(id_edificio: int, db: Session = Depends(get_session)):
    """
    Promedio histórico por mes (1-12).
    """
    return service.estacionalidad(db, id_edificio)


# ------------------------------------------------------------
# 6) Ranking de meses con mayor consumo
# ------------------------------------------------------------
@router.get("/ranking/{id_edificio}")
def ranking_consumo(
    id_edificio: int,
    top: int = Query(5, ge=1, le=50),
    db: Session = Depends(get_session)
):
    """
    Ranking de los meses con mayor consumo.
    """
    return service.ranking_meses(db, id_edificio, top)


# ------------------------------------------------------------
# 7) Tendencia de consumo (rolling mean)
# ------------------------------------------------------------
@router.get("/tendencia/{id_edificio}")
def tendencia(
    id_edificio: int,
    window: int = Query(3, ge=1, le=12),
    db: Session = Depends(get_session)
):
    """
    Tendencia de consumo usando media móvil.
    """
    return service.tendencia(db, id_edificio, window)


# ------------------------------------------------------------
# 8) Año de mayor consumo
# ------------------------------------------------------------
@router.get("/anio-mayor-consumo/{id_edificio}")
def anio_mayor_consumo(id_edificio: int, db: Session = Depends(get_session)):
    """
    Devuelve el año con mayor consumo.
    """
    return service.anio_mayor_consumo(db, id_edificio)


# ------------------------------------------------------------
# 9) Cálculo de potencial de ahorro
# ------------------------------------------------------------
@router.get("/ahorro-potencial/{id_edificio}")
def ahorro_potencial(id_edificio: int, db: Session = Depends(get_session)):
    """
    Calcula el ahorro potencial del 10%.
    """
    return service.potencial_ahorro(db, id_edificio)