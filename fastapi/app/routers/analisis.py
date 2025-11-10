# app/routers/analisis.py
from fastapi import APIRouter, Query
from app.db.queries import obtener_consumo_total

router = APIRouter(prefix="/analisis", tags=["Análisis"])

@router.get("/consumo")
def consumo_por_anio(anio: int, id_sector: int | None = None, id_dependencia: int | None = None):
    datos = obtener_consumo_total(anio, id_sector, id_dependencia)
    return {"anio": anio, "resultados": datos}
