# ============================================================
#  app/services/analisis_service.py
#  Análisis Energético. CORREGIDO a sintaxis SQLAlchemy 2.0
# ============================================================

from sqlalchemy.orm import Session
from sqlalchemy import func, select
from app.db.models import ConsumoHistorico
from typing import Dict, List
import pandas as pd


# ============================================================
#  UTILERÍA
# ============================================================

def _df_from_query(query_results):
    """Convierte resultados de consulta 2.0 (Rows) a DataFrame."""
    if not query_results:
        return pd.DataFrame()
    
    # Mapeo a diccionario para Pandas
    data = [dict(r._mapping) for r in query_results]
    
    df = pd.DataFrame(data)
    if "consumo_kwh" in df.columns:
        df["consumo_kwh"] = pd.to_numeric(df["consumo_kwh"])
    if "costo_total" in df.columns:
        df["costo_total"] = pd.to_numeric(df["costo_total"])
        
    return df


# ============================================================
# 1) CONSUMO TOTAL ANUAL
# ============================================================

def consumo_total_anual(db: Session, id_edificio: int) -> Dict:
    # Usa select() y where() para SQA 2.0
    stmt = (
        select(
            ConsumoHistorico.anio,
            func.sum(ConsumoHistorico.consumo_kwh).label("total_kwh")
        )
        .where(ConsumoHistorico.edificio_id == id_edificio)
        .group_by(ConsumoHistorico.anio)
        .order_by(ConsumoHistorico.anio)
    )
    results = db.execute(stmt).all()
    return {r.anio: float(r.total_kwh) for r in results}


# ============================================================
# 2) CONSUMO MENSUAL (para un año específico)
# ============================================================

def consumo_mensual(db: Session, id_edificio: int, anio: int) -> Dict:
    stmt = (
        select(
            ConsumoHistorico.mes,
            ConsumoHistorico.consumo_kwh
        )
        .where(
            ConsumoHistorico.edificio_id == id_edificio,
            ConsumoHistorico.anio == anio
        )
        .order_by(ConsumoHistorico.mes)
    )
    results = db.execute(stmt).all()
    return {m.mes: float(m.consumo_kwh) for m in results}


# ============================================================
# 3) COSTO TOTAL ANUAL
# ============================================================

def costo_total_anual(db: Session, id_edificio: int) -> Dict:
    stmt = (
        select(
            ConsumoHistorico.anio,
            func.sum(ConsumoHistorico.costo_total).label("costo_anual")
        )
        .where(ConsumoHistorico.edificio_id == id_edificio)
        .group_by(ConsumoHistorico.anio)
        .order_by(ConsumoHistorico.anio)
    )
    results = db.execute(stmt).all()
    return {r.anio: float(r.costo_anual) for r in results}


# ============================================================
# 4) CONSUMO PROMEDIO POR AÑO
# ============================================================

def consumo_promedio_anual(db: Session, id_edificio: int) -> Dict:
    stmt = (
        select(
            ConsumoHistorico.anio,
            func.avg(ConsumoHistorico.consumo_kwh).label("promedio_kwh")
        )
        .where(ConsumoHistorico.edificio_id == id_edificio)
        .group_by(ConsumoHistorico.anio)
        .order_by(ConsumoHistorico.anio)
    )
    results = db.execute(stmt).all()
    return {r.anio: float(r.promedio_kwh) for r in results}


# ============================================================
# 5) ESTACIONALIDAD (promedio por MES en todos los años)
# ============================================================

def estacionalidad(db: Session, id_edificio: int) -> Dict:
    stmt = (
        select(
            ConsumoHistorico.mes,
            func.avg(ConsumoHistorico.consumo_kwh).label("promedio_mes")
        )
        .where(ConsumoHistorico.edificio_id == id_edificio)
        .group_by(ConsumoHistorico.mes)
        .order_by(ConsumoHistorico.mes)
    )
    results = db.execute(stmt).all()
    return {r.mes: float(r.promedio_mes) for r in results}


# ============================================================
# 6) TOP MESES DE MAYOR CONSUMO (ranking)
# ============================================================

def ranking_meses(db: Session, id_edificio: int, top: int = 5) -> List[Dict]:
    stmt = (
        select(
            ConsumoHistorico.anio,
            ConsumoHistorico.mes,
            ConsumoHistorico.consumo_kwh
        )
        .where(ConsumoHistorico.edificio_id == id_edificio)
        .order_by(ConsumoHistorico.consumo_kwh.desc())
        .limit(top)
    )
    results = db.execute(stmt).all()
    return [
        {
            "anio": r.anio,
            "mes": r.mes,
            "consumo_kwh": float(r.consumo_kwh)
        }
        for r in results
    ]


# ============================================================
# 7) TENDENCIA (rolling mean)
# ============================================================

def tendencia(db: Session, id_edificio: int, window: int = 3) -> List[Dict]:
    stmt = (
        select(
            ConsumoHistorico.anio,
            ConsumoHistorico.mes,
            ConsumoHistorico.consumo_kwh,
            ConsumoHistorico.costo_total
        )
        .where(ConsumoHistorico.edificio_id == id_edificio)
        .order_by(ConsumoHistorico.anio, ConsumoHistorico.mes)
    )
    registros = db.execute(stmt).all() 

    df = _df_from_query(registros)
    if df.empty:
        return []

    df["tendencia"] = df["consumo_kwh"].rolling(window=window, min_periods=1).mean()
    df = df.where(pd.notnull(df), None)
    
    return df.to_dict(orient="records")


# ============================================================
# 8) AÑO CON MAYOR CONSUMO
# ============================================================

def anio_mayor_consumo(db: Session, id_edificio: int) -> Dict:
    stmt = (
        select(
            ConsumoHistorico.anio,
            func.sum(ConsumoHistorico.consumo_kwh).label("total")
        )
        .where(ConsumoHistorico.edificio_id == id_edificio)
        .group_by(ConsumoHistorico.anio)
        .order_by(func.sum(ConsumoHistorico.consumo_kwh).desc())
    )
    result = db.execute(stmt).first()

    if not result:
        return {}

    return {"anio": result.anio, "total_kwh": float(result.total)}


# ============================================================
# 9) POTENCIAL DE AHORRO (reducción del 10%)
# ============================================================

def potencial_ahorro(db: Session, id_edificio: int) -> Dict:
    stmt = (
        select(func.sum(ConsumoHistorico.consumo_kwh))
        .where(ConsumoHistorico.edificio_id == id_edificio)
    )
    total = db.execute(stmt).scalar()

    if not total:
        return {}
    
    total_float = float(total)
    ahorro_10 = total_float * 0.10

    return {
        "consumo_actual": total_float,
        "ahorro_potencial_kwh": ahorro_10,
        "consumo_proyectado": total_float - ahorro_10,
    }


# # ============================================================
# #  app/services/analisis_service.py
# #  Análisis Energético Real basado en consumo_historico
# # ============================================================

# from sqlalchemy.orm import Session
# from sqlalchemy import func,select
# from app.db.models import ConsumoHistorico
# from typing import Dict, List
# import pandas as pd


# # ============================================================
# #  UTILERÍA
# # ============================================================

# def _df_from_query(query_results):
#     """Convierte resultados ORM a DataFrame."""
#     if not query_results:
#         return pd.DataFrame()

#     data = [
#         {
#             "anio": r.anio,
#             "mes": r.mes,
#             "consumo_kwh": float(r.consumo_kwh),
#             "costo_total": float(r.costo_total),
#         }
#         for r in query_results
#     ]
#     return pd.DataFrame(data)


# # ============================================================
# # 1) CONSUMO TOTAL ANUAL
# # ============================================================

# def consumo_total_anual(db: Session, id_edificio: int) -> Dict:
#     results = (
#         db.query(
#             ConsumoHistorico.anio,
#             func.sum(ConsumoHistorico.consumo_kwh).label("total_kwh")
#         )
#         .filter(ConsumoHistorico.edificio_id == id_edificio)
#         .group_by(ConsumoHistorico.anio)
#         .order_by(ConsumoHistorico.anio)
#         .all()
#     )

#     return {r.anio: float(r.total_kwh) for r in results}


# # ============================================================
# # 2) CONSUMO MENSUAL (para un año específico)
# # ============================================================

# def consumo_mensual(db: Session, id_edificio: int, anio: int) -> Dict:
#     results = (
#         db.query(
#             ConsumoHistorico.mes,
#             ConsumoHistorico.consumo_kwh
#         )
#         .filter(
#             ConsumoHistorico.edificio_id == id_edificio,
#             ConsumoHistorico.anio == anio
#         )
#         .order_by(ConsumoHistorico.mes)
#         .all()
#     )

#     return {m.mes: float(m.consumo_kwh) for m in results}


# # ============================================================
# # 3) COSTO TOTAL ANUAL
# # ============================================================

# def costo_total_anual(db: Session, id_edificio: int) -> Dict:
#     results = (
#         db.query(
#             ConsumoHistorico.anio,
#             func.sum(ConsumoHistorico.costo_total).label("costo_anual")
#         )
#         .filter(ConsumoHistorico.edificio_id == id_edificio)
#         .group_by(ConsumoHistorico.anio)
#         .order_by(ConsumoHistorico.anio)
#         .all()
#     )

#     return {r.anio: float(r.costo_anual) for r in results}


# # ============================================================
# # 4) CONSUMO PROMEDIO POR AÑO
# # ============================================================

# def consumo_promedio_anual(db: Session, id_edificio: int) -> Dict:
#     results = (
#         db.query(
#             ConsumoHistorico.anio,
#             func.avg(ConsumoHistorico.consumo_kwh).label("promedio_kwh")
#         )
#         .filter(ConsumoHistorico.edificio_id == id_edificio)
#         .group_by(ConsumoHistorico.anio)
#         .order_by(ConsumoHistorico.anio)
#         .all()
#     )

#     return {r.anio: float(r.promedio_kwh) for r in results}


# # ============================================================
# # 5) ESTACIONALIDAD (promedio por MES en todos los años)
# # ============================================================

# def estacionalidad(db: Session, id_edificio: int) -> Dict:
#     results = (
#         db.query(
#             ConsumoHistorico.mes,
#             func.avg(ConsumoHistorico.consumo_kwh).label("promedio_mes")
#         )
#         .filter(ConsumoHistorico.edificio_id == id_edificio)
#         .group_by(ConsumoHistorico.mes)
#         .order_by(ConsumoHistorico.mes)
#         .all()
#     )

#     return {r.mes: float(r.promedio_mes) for r in results}


# # ============================================================
# # 6) TOP MESES DE MAYOR CONSUMO (ranking)
# # ============================================================

# def ranking_meses(db: Session, id_edificio: int, top: int = 5) -> List[Dict]:
#     results = (
#         db.query(
#             ConsumoHistorico.anio,
#             ConsumoHistorico.mes,
#             ConsumoHistorico.consumo_kwh
#         )
#         .filter(ConsumoHistorico.edificio_id == id_edificio)
#         .order_by(ConsumoHistorico.consumo_kwh.desc())
#         .limit(top)
#         .all()
#     )

#     return [
#         {
#             "anio": r.anio,
#             "mes": r.mes,
#             "consumo_kwh": float(r.consumo_kwh)
#         }
#         for r in results
#     ]


# # ============================================================
# # 7) TENDENCIA (rolling mean)
# # ============================================================

# def tendencia(db: Session, id_edificio: int, window: int = 3) -> List[Dict]:
#     # Seleccionamos solo las columnas necesarias para el DataFrame
#     stmt = (
#         select(
#             ConsumoHistorico.anio,
#             ConsumoHistorico.mes,
#             ConsumoHistorico.consumo_kwh,
#             ConsumoHistorico.costo_total
#         )
#         .where(ConsumoHistorico.edificio_id == id_edificio)
#         .order_by(ConsumoHistorico.anio, ConsumoHistorico.mes)
#     )
#     registros = db.execute(stmt).all() # <-- Esta consulta NO pide el 'id'

#     df = _df_from_query(registros)
#     if df.empty:
#         return []

#     df["tendencia"] = df["consumo_kwh"].rolling(window=window, min_periods=1).mean()
    
#     # Convertir floats de NaN a None para compatibilidad JSON
#     df = df.where(pd.notnull(df), None)
    
#     return df.to_dict(orient="records")


# # ============================================================
# # 8) AÑO CON MAYOR CONSUMO
# # ============================================================

# def anio_mayor_consumo(db: Session, id_edificio: int) -> Dict:
#     result = (
#         db.query(
#             ConsumoHistorico.anio,
#             func.sum(ConsumoHistorico.consumo_kwh).label("total")
#         )
#         .filter(ConsumoHistorico.edificio_id == id_edificio)
#         .group_by(ConsumoHistorico.anio)
#         .order_by(func.sum(ConsumoHistorico.consumo_kwh).desc())
#         .first()
#     )

#     if not result:
#         return {}

#     return {"anio": result.anio, "total_kwh": float(result.total)}


# # ============================================================
# # 9) POTENCIAL DE AHORRO (reducción del 10%)
# # ============================================================

# def potencial_ahorro(db: Session, id_edificio: int) -> Dict:
#     stmt = (
#         select(func.sum(ConsumoHistorico.consumo_kwh))
#         .where(ConsumoHistorico.edificio_id == id_edificio)
#     )
#     # total aquí es un objeto 'Decimal' de la base de datos
#     total = db.execute(stmt).scalar()

#     if not total:
#         return {}
    
   
#     total_float = float(total)
    
#     # Ahora usa el float para todas las operaciones
#     ahorro_10 = total_float * 0.10

#     return {
#         "consumo_actual": total_float,
#         "ahorro_potencial_kwh": ahorro_10,
#         "consumo_proyectado": total_float - ahorro_10,
#     }
