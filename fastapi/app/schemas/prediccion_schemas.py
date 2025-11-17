# app/schemas/prediccion_schemas.py

from pydantic import BaseModel, Field
from typing import Optional, Dict


class WhatIfInput(BaseModel):
    meses_a_predecir: int = Field(3, description="Número de meses a predecir")
    variacion_consumo: Optional[float] = Field(
        None, description="Variación porcentual (ej: 0.10 = +10%, -0.15 = -15%)"
    )
    variacion_tarifa: Optional[float] = Field(
        None, description="Variación porcentual de tarifa"
    )
    tarifas_personalizadas: Optional[Dict[str, float]] = Field(
        None,
        description="Diccionario con tarifas por mes: {'2025-01': 4.23}"
    )
