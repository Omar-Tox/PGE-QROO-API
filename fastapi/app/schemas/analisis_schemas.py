# app/schemas/analisis_schemas.py

from pydantic import BaseModel
from typing import List, Optional


# ================================
# 📌 Consumo total anual
# ================================
class ConsumoTotalAnualItem(BaseModel):
    edificio: str
    consumo_kwh: float
    costo_total: float


class ConsumoTotalAnualResponse(BaseModel):
    anio: int
    total_consumo_kwh: float
    total_costo: float
    resultados: List[ConsumoTotalAnualItem]


# ================================
# 📌 Consumo mensual por edificio
# ================================
class ConsumoMensualItem(BaseModel):
    mes: int
    consumo_kwh: float
    costo_total: float


class ConsumoEdificioMensualResponse(BaseModel):
    id_edificio: int
    anio: int
    edificio: str
    datos: List[ConsumoMensualItem]


# ================================
# 📌 Ranking (Top / Low)
# ================================
class RankingItem(BaseModel):
    id_edificio: int
    edificio: str
    total_consumo_kwh: float
    total_costo: float


class RankingResponse(BaseModel):
    anio: int
    tipo: str  # "mayor_consumo", "menor_consumo", "mayor_ahorro", etc.
    resultados: List[RankingItem]


# ================================
# 📌 Comparativa año contra año
# ================================
class ComparativaAnioItem(BaseModel):
    id_edificio: int
    edificio: str
    consumo_anio_actual: float
    consumo_anio_pasado: float
    variacion_kwh: float
    variacion_porcentaje: float


class ComparativaAnualResponse(BaseModel):
    anio_actual: int
    anio_pasado: int
    resultados: List[ComparativaAnioItem]


# ================================
# 📌 Filtros estándar para análisis
# (Opcional — se usa en endpoints con Query)
# ================================
class FiltrosAnalisis(BaseModel):
    anio: int
    id_sector: Optional[int] = None
    id_dependencia: Optional[int] = None
