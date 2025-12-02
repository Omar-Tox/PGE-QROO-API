
# ============================================================
#  app/routers/analisis_publico.py
#  Router inteligente para vistas públicas y comparativas
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.connection import get_session
from app.services import analisis_service as service
from app.schemas.analisis_schemas import RespuestaComparativa

router = APIRouter(
    prefix="/analisis/publico",
    tags=["Análisis Público (Gráficas)"]
)

def _parsear_ids(ids_str: str) -> List[int]:
    """Convierte string '1,2,3' en lista [1, 2, 3]."""
    try:
        lista = [int(x) for x in ids_str.split(",") if x.strip()]
        if not lista:
            raise ValueError
        return lista
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de IDs inválido. Use '1,2,3'")

# ------------------------------------------------------------------
# 1. Comparativa de Consumo (kWh) - Líneas
# ------------------------------------------------------------------
@router.get("/comparativa-consumo", response_model=RespuestaComparativa)
def obtener_comparativa_consumo(
    anio: int,
    ids: str = Query(..., description="Lista de IDs (ej. '1,2,3')"),
    tipo_filtro: str = Query(..., regex="^(edificio|dependencia|sector)$"),
    db: Session = Depends(get_session)
):
    lista_ids = _parsear_ids(ids)
    ids_finales = service.resolver_ids_por_filtro(db, tipo_filtro, lista_ids)
    
    # Limite de seguridad visual
    if len(ids_finales) > 20: ids_finales = ids_finales[:20]

    return service.comparativa_consumo_mensual(db, ids_finales, anio)

# ------------------------------------------------------------------
# 2. Comparativa de Costos ($) - Líneas
# ------------------------------------------------------------------
@router.get("/comparativa-costos", response_model=RespuestaComparativa)
def obtener_comparativa_costos(
    anio: int,
    ids: str = Query(..., description="Lista de IDs (ej. '1,2,3')"),
    tipo_filtro: str = Query(..., regex="^(edificio|dependencia|sector)$"),
    db: Session = Depends(get_session)
):
    lista_ids = _parsear_ids(ids)
    ids_finales = service.resolver_ids_por_filtro(db, tipo_filtro, lista_ids)
    
    if len(ids_finales) > 20: ids_finales = ids_finales[:20]

    return service.comparativa_costo_mensual(db, ids_finales, anio)

# ------------------------------------------------------------------
# 3. Ranking (Top Consumidores) - Barras
# ------------------------------------------------------------------
@router.get("/ranking", response_model=RespuestaComparativa)
def obtener_ranking_publico(
    anio: int,
    ids: str = Query(..., description="Lista de IDs (ej. '1,2,3')"),
    tipo_filtro: str = Query(..., regex="^(edificio|dependencia|sector)$"),
    db: Session = Depends(get_session)
):
    """Devuelve los edificios con mayor consumo dentro del filtro seleccionado."""
    lista_ids = _parsear_ids(ids)
    ids_finales = service.resolver_ids_por_filtro(db, tipo_filtro, lista_ids)
    
    return service.ranking_publico(db, ids_finales, anio)


# ------------------------------------------------------------------
# 4. Presupuesto vs Gasto (Trimestral)
# ------------------------------------------------------------------
@router.get("/presupuesto-vs-gasto", response_model=RespuestaComparativa)
def obtener_presupuesto_vs_gasto(
    anio: int,
    ids: str = Query(..., description="Lista de IDs (ej. '1,2,3')"),
    tipo_filtro: str = Query(..., regex="^(edificio|dependencia|sector)$"),
    db: Session = Depends(get_session)
):
    """
    Compara cuánto presupuesto tenían las dependencias vs cuánto gastaron en energía.
    Si el filtro es 'edificio', se comparará el gasto del edificio vs el presupuesto de su dependencia padre.
    """
    lista_ids = _parsear_ids(ids)
    
    # 1. Resolver qué dependencias están involucradas (Usamos la nueva función del servicio)
    ids_dependencias = service.resolver_ids_dependencias_por_filtro(db, tipo_filtro, lista_ids)
    
    if not ids_dependencias:
         return {
            "titulo": "No se encontraron dependencias relacionadas",
            "eje_x": [],
            "series": []
        }

    return service.analisis_presupuestal_trimestral(db, ids_dependencias, anio)