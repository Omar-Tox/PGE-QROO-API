# app/schemas/analisis_schemas.py

from pydantic import BaseModel
from typing import List, Optional, Any


# ================================
#  Consumo total anual
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
#  Consumo mensual por edificio
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
#  Ranking (Top / Low)
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
#  Comparativa año contra año
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
#  Filtros estándar para análisis
# ================================
class FiltrosAnalisis(BaseModel):
    anio: int
    id_sector: Optional[int] = None
    id_dependencia: Optional[int] = None


# =========================================================
# NUEVOS SCHEMAS PARA GRÁFICAS (COMPARATIVAS PÚBLICAS)
# =========================================================
class SerieDatos(BaseModel):
    """Representa una línea o barra en la gráfica."""
    nombre: str              
    datos: List[float]       
    color: Optional[str] = None 

class RespuestaComparativa(BaseModel):
    """Estructura final que consume Chart.js o ApexCharts."""
    titulo: str
    eje_x: List[str]         
    series: List[SerieDatos] 

#  NUEVO: Para métricas de presupuesto
class MetricaPresupuestal(BaseModel):
    anio: int
    presupuesto_total: float
    gasto_total_energia: float
    porcentaje_ejecutado: float # Cuánto del presupuesto se fue en luz
    ahorro_o_deficit: float
# =========================================================
# 🆕 NUEVO SCHEMA: KPIs Reales del Dashboard Privado
# =========================================================

class DashboardKpisResponse(BaseModel):
    anio: int
    
    # Métricas de Consumo
    total_kwh: float
    promedio_kwh: float
    
    # Análisis Financiero Real
    costo_total_energia: float      # Lo que se pagó a CFE
    presupuesto_asignado: float     # Dinero que tenía la dependencia
    balance_financiero: float       # (Presupuesto - Costo) -> Si es negativo, gastaron de más
    estado_presupuestal: str        # "Superávit" o "Déficit"
    
    # Contexto (Origen de los datos)
    dependencias_involucradas: List[str] # Nombres de las dependencias analizada
    
    
    

# =========================================================
# 🆕 NUEVO SCHEMA: KPIs Reales del Dashboard Privado
# =========================================================

class DashboardKpisResponse(BaseModel):
    anio: int
    total_kwh: float
    promedio_kwh: float
    costo_total_energia: float
    presupuesto_asignado: float
    balance_financiero: float
    estado_presupuestal: str
    dependencias_involucradas: List[str]

# =========================================================
# 🆕 SCHEMAS PARA GRÁFICAS PRIVADAS (CON CONTEXTO)
# =========================================================

class DashboardEvolucionResponse(BaseModel):
    anio: int
    eje_x: List[str]
    serie_consumo_kwh: List[float]
    serie_costo: List[float]
    dependencias_involucradas: List[str]

class DashboardTendenciaItem(BaseModel):
    anio: int
    mes: int
    consumo_kwh: float
    tendencia: Optional[float]

class DashboardTendenciaResponse(BaseModel):
    historico: List[DashboardTendenciaItem]
    dependencias_involucradas: List[str]

class DashboardRankingResponse(BaseModel):
    nombres: List[str]
    valores: List[float]
    dependencias_involucradas: List[str]

# =========================================================
# 🆕 SCHEMAS PARA GRÁFICAS PÚBLICAS
# =========================================================

class SerieDatos(BaseModel):
    nombre: str
    datos: List[float]
    color: Optional[str] = None

class RespuestaComparativa(BaseModel):
    titulo: str
    eje_x: List[str]
    series: List[SerieDatos]
    dependencias_involucradas: List[str] = [] # Nuevo campo con valor por defecto
# # app/schemas/analisis_schemas.py

# from pydantic import BaseModel
# from typing import List, Optional


# # ================================
# # 📌 Consumo total anual
# # ================================
# class ConsumoTotalAnualItem(BaseModel):
#     edificio: str
#     consumo_kwh: float
#     costo_total: float


# class ConsumoTotalAnualResponse(BaseModel):
#     anio: int
#     total_consumo_kwh: float
#     total_costo: float
#     resultados: List[ConsumoTotalAnualItem]


# # ================================
# # 📌 Consumo mensual por edificio
# # ================================
# class ConsumoMensualItem(BaseModel):
#     mes: int
#     consumo_kwh: float
#     costo_total: float


# class ConsumoEdificioMensualResponse(BaseModel):
#     id_edificio: int
#     anio: int
#     edificio: str
#     datos: List[ConsumoMensualItem]


# # ================================
# # 📌 Ranking (Top / Low)
# # ================================
# class RankingItem(BaseModel):
#     id_edificio: int
#     edificio: str
#     total_consumo_kwh: float
#     total_costo: float


# class RankingResponse(BaseModel):
#     anio: int
#     tipo: str  # "mayor_consumo", "menor_consumo", "mayor_ahorro", etc.
#     resultados: List[RankingItem]


# # ================================
# # 📌 Comparativa año contra año
# # ================================
# class ComparativaAnioItem(BaseModel):
#     id_edificio: int
#     edificio: str
#     consumo_anio_actual: float
#     consumo_anio_pasado: float
#     variacion_kwh: float
#     variacion_porcentaje: float


# class ComparativaAnualResponse(BaseModel):
#     anio_actual: int
#     anio_pasado: int
#     resultados: List[ComparativaAnioItem]


# # ================================
# # 📌 Filtros estándar para análisis
# # (Opcional — se usa en endpoints con Query)
# # ================================
# class FiltrosAnalisis(BaseModel):
#     anio: int
#     id_sector: Optional[int] = None
#     id_dependencia: Optional[int] = None
