# app/routers/prediccion_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db


from app.services.prediccion_service import PrediccionService
from app.schemas.prediccion_schemas import WhatIfInput

router = APIRouter(prefix="/prediccion", tags=["Predicción"])


# =====================================================
# 🔹 1) Predicción de consumo
# =====================================================
@router.get("/consumo/{id_edificio}")
async def prediccion_consumo(
    id_edificio: int,
    db: AsyncSession = Depends(get_db)
):
    resultado = await PrediccionService.predecir_consumo(db, id_edificio)
    return resultado


# =====================================================
# 🔹 2) Predicción de costos
# =====================================================
@router.get("/costos/{id_edificio}")
async def prediccion_costos(
    id_edificio: int,
    db: AsyncSession = Depends(get_db)
):
    resultado = await PrediccionService.predecir_costos(db, id_edificio)
    return resultado


# =====================================================
# 🔹 3) WHAT-IF (POST por parámetros variables)
# =====================================================
@router.post("/what-if/{id_edificio}")
async def prediccion_what_if(
    id_edificio: int,
    payload: WhatIfInput,
    db: AsyncSession = Depends(get_db)
):

    resultado = await PrediccionService.what_if(
        db=db,
        id_edificio=id_edificio,
        meses_a_predecir=payload.meses_a_predecir,
        variacion_consumo=payload.variacion_consumo,
        variacion_tarifa=payload.variacion_tarifa,
        tarifas_personalizadas=payload.tarifas_personalizadas
    )

    return resultado
