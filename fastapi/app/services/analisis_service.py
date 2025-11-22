# ============================================================
#  app/services/analisis_service.py
#  Versión Final: Lógica completa para análisis energético y financiero
# ============================================================
# ============================================================
#  app/services/analisis_service.py
#  Versión Final: Lógica completa para análisis energético y financiero
# ============================================================

from sqlalchemy.orm import Session
from sqlalchemy import func, select, desc
from app.db.models import ConsumoHistorico, Edificio, Dependencia, Sector, Presupuesto
from typing import Dict, List, Any
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
#  FUNCIONES EXISTENTES (Single ID)
# ============================================================

def consumo_total_anual(db: Session, id_edificio: int) -> Dict:
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


# ============================================================
#  🚀 NUEVAS FUNCIONES PARA VISTA PÚBLICA (COMPARATIVAS)
# ============================================================

def resolver_ids_por_filtro(db: Session, tipo: str, ids_solicitados: List[int]) -> List[int]:
    """
    Convierte la selección del usuario (Sector/Dependencia) en una lista de IDs de edificios.
    """
    if tipo == "edificio":
        return ids_solicitados  # Ya son edificios
    
    if tipo == "dependencia":
        # Buscar todos los edificios de estas dependencias
        stmt = select(Edificio.id_edificio).where(Edificio.dependencia_id.in_(ids_solicitados))
        return db.execute(stmt).scalars().all()
    
    if tipo == "sector":
        # Buscar dependencias del sector -> luego edificios
        # JOIN Edificio -> Dependencia -> Sector
        stmt = (
            select(Edificio.id_edificio)
            .join(Edificio.dependencia)
            .where(Dependencia.sector_id.in_(ids_solicitados))
        )
        return db.execute(stmt).scalars().all()
    
    return []


def _generar_respuesta_comparativa(
    db: Session, 
    ids_edificios: List[int], 
    datos_raw: List[Any], 
    titulo: str,
    es_costo: bool = False
) -> Dict:
    """Helper interno para formatear respuestas de gráficas."""
    stmt_nombres = select(Edificio.id_edificio, Edificio.nombre_edificio).where(Edificio.id_edificio.in_(ids_edificios))
    nombres_map = {row.id_edificio: row.nombre_edificio for row in db.execute(stmt_nombres)}

    # Eje X estándar de meses
    eje_x = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    
    series_dict = {id_ed: [0.0] * 12 for id_ed in ids_edificios}

    for fila in datos_raw:
        if 1 <= fila.mes <= 12:
            valor = float(fila.costo_total) if es_costo else float(fila.consumo_kwh)
            series_dict[fila.edificio_id][fila.mes - 1] = valor

    lista_series = []
    for id_ed, data_mensual in series_dict.items():
        lista_series.append({
            "nombre": nombres_map.get(id_ed, f"Edificio {id_ed}"),
            "datos": data_mensual,
            "color": None 
        })

    return {
        "titulo": titulo,
        "eje_x": eje_x,
        "series": lista_series
    }


def comparativa_consumo_mensual(db: Session, ids_edificios: List[int], anio: int) -> Dict:
    """
    Genera la estructura para gráficas multi-serie (Chart.js).
    Compara el consumo mensual de varios edificios en un año específico.
    """
    if not ids_edificios:
        return {"titulo": "Sin datos", "eje_x": [], "series": []}

    # Obtener datos de consumo
    stmt = (
        select(
            ConsumoHistorico.edificio_id,
            ConsumoHistorico.mes,
            ConsumoHistorico.consumo_kwh
        )
        .where(
            ConsumoHistorico.edificio_id.in_(ids_edificios),
            ConsumoHistorico.anio == anio
        )
        .order_by(ConsumoHistorico.mes)
    )
    datos = db.execute(stmt).all()

    return _generar_respuesta_comparativa(db, ids_edificios, datos, f"Comparativa Consumo (kWh) {anio}")


def comparativa_costo_mensual(db: Session, ids_edificios: List[int], anio: int) -> Dict:
    if not ids_edificios:
        return {"titulo": "Sin datos", "eje_x": [], "series": []}

    stmt = (
        select(ConsumoHistorico.edificio_id, ConsumoHistorico.mes, ConsumoHistorico.costo_total)
        .where(ConsumoHistorico.edificio_id.in_(ids_edificios), ConsumoHistorico.anio == anio)
        .order_by(ConsumoHistorico.mes)
    )
    datos = db.execute(stmt).all()
    return _generar_respuesta_comparativa(db, ids_edificios, datos, f"Comparativa Costos ($) {anio}", es_costo=True)


def ranking_publico(db: Session, ids_edificios: List[int], anio: int) -> Dict:
    """Top edificios con mayor consumo en el año seleccionado."""
    if not ids_edificios:
        return {"titulo": "Sin datos", "eje_x": [], "series": []}

    # Top 10
    stmt = (
        select(
            ConsumoHistorico.edificio_id,
            func.sum(ConsumoHistorico.consumo_kwh).label("total")
        )
        .where(ConsumoHistorico.edificio_id.in_(ids_edificios), ConsumoHistorico.anio == anio)
        .group_by(ConsumoHistorico.edificio_id)
        .order_by(desc("total"))
        .limit(10)
    )
    resultados = db.execute(stmt).all()
    
    # Obtener nombres
    ids_top = [r.edificio_id for r in resultados]
    stmt_nombres = select(Edificio.id_edificio, Edificio.nombre_edificio).where(Edificio.id_edificio.in_(ids_top))
    nombres_map = {row.id_edificio: row.nombre_edificio for row in db.execute(stmt_nombres)}

    # Formato especial para gráfica de barras (Ranking)
    # Eje X: Nombres de edificios
    # Serie: Un solo conjunto de datos
    eje_x = [nombres_map.get(r.edificio_id, str(r.edificio_id)) for r in resultados]
    datos = [float(r.total) for r in resultados]

    return {
        "titulo": f"Top Consumo {anio}",
        "eje_x": eje_x,
        "series": [{
            "nombre": "Total kWh",
            "datos": datos,
            "color": None
        }]
    }


# ============================================================
#  💰 NUEVAS FUNCIONES: PRESUPUESTO VS GASTO
# ============================================================

def resolver_ids_dependencias_por_filtro(db: Session, tipo: str, ids_solicitados: List[int]) -> List[int]:
    """
    Similar a resolver edificios, pero devuelve IDs de DEPENDENCIAS.
    Necesario porque el presupuesto está ligado a la Dependencia, no al edificio.
    """
    if tipo == "dependencia":
        return ids_solicitados
    
    if tipo == "sector":
        # Traer todas las dependencias de estos sectores
        stmt = select(Dependencia.id_dependencia).where(Dependencia.sector_id.in_(ids_solicitados))
        return db.execute(stmt).scalars().all()
    
    if tipo == "edificio":
        # Traer las dependencias padres de estos edificios
        stmt = select(Edificio.dependencia_id).where(Edificio.id_edificio.in_(ids_solicitados)).distinct()
        return db.execute(stmt).scalars().all()
        
    return []

def analisis_presupuestal_trimestral(db: Session, ids_dependencias: List[int], anio: int) -> Dict:
    """
    Compara Trimestre a Trimestre: Dinero Asignado (Dependencia) vs Gasto Real (Suma de Edificios).
    """
    if not ids_dependencias:
        return {"titulo": "Sin datos", "eje_x": [], "series": []}

    # 1. Obtener Presupuesto (Agrupado por Trimestre)
    stmt_presu = (
        select(
            Presupuesto.trimestre,
            func.sum(Presupuesto.monto_asignado).label("total_asignado")
        )
        .where(
            Presupuesto.dependencia_id.in_(ids_dependencias),
            Presupuesto.anio == anio
        )
        .group_by(Presupuesto.trimestre)
        .order_by(Presupuesto.trimestre)
    )
    data_presu = db.execute(stmt_presu).all()

    # 2. Obtener Gasto Real (Sumando consumo de todos los edificios de esas dependencias)
    # Usamos JOIN explícito: ConsumoHistorico -> Edificio (donde edificio.dependencia_id está en la lista)
    stmt_gasto = (
        select(
            ConsumoHistorico.mes,
            func.sum(ConsumoHistorico.costo_total).label("gasto_mes")
        )
        .join(ConsumoHistorico.edificio) # Join con la tabla Edificio
        .where(
            Edificio.dependencia_id.in_(ids_dependencias), # Filtramos por la dependencia dueña del edificio
            ConsumoHistorico.anio == anio
        )
        .group_by(ConsumoHistorico.mes)
    )
    data_gasto = db.execute(stmt_gasto).all()

    # 3. Procesar y Alinear Datos (Meses -> Trimestres)
    trimestres = {
        1: {"presupuesto": 0.0, "gasto": 0.0}, 
        2: {"presupuesto": 0.0, "gasto": 0.0}, 
        3: {"presupuesto": 0.0, "gasto": 0.0}, 
        4: {"presupuesto": 0.0, "gasto": 0.0}
    }

    # Llenar Presupuesto
    for fila in data_presu:
        if 1 <= fila.trimestre <= 4:
            trimestres[fila.trimestre]["presupuesto"] = float(fila.total_asignado)

    # Llenar Gasto (Sumando meses al trimestre correspondiente)
    for fila in data_gasto:
        trim = (fila.mes - 1) // 3 + 1  # Formula mágica: mes 1-3->1, 4-6->2...
        if 1 <= trim <= 4:
            trimestres[trim]["gasto"] += float(fila.gasto_mes)

    # 4. Formatear para Gráfica
    eje_x = ["Trimestre 1", "Trimestre 2", "Trimestre 3", "Trimestre 4"]
    serie_presupuesto = [trimestres[t]["presupuesto"] for t in [1,2,3,4]]
    serie_gasto = [trimestres[t]["gasto"] for t in [1,2,3,4]]

    return {
        "titulo": f"Presupuesto vs Gasto Energético {anio}",
        "eje_x": eje_x,
        "series": [
            {
                "nombre": "Presupuesto Asignado",
                "datos": serie_presupuesto,
                "color": "#28a745" # Verde (Dinero disponible)
            },
            {
                "nombre": "Gasto en Energía",
                "datos": serie_gasto,
                "color": "#dc3545" # Rojo (Dinero que sale)
            }
        ]
    }
# from sqlalchemy.orm import Session
# from sqlalchemy import func, select, desc
# from app.db.models import ConsumoHistorico, Edificio, Dependencia, Sector, Presupuesto
# from typing import Dict, List, Any
# import pandas as pd


# # ============================================================
# #  UTILERÍA
# # ============================================================

# def _df_from_query(query_results):
#     """Convierte resultados de consulta 2.0 (Rows) a DataFrame."""
#     if not query_results:
#         return pd.DataFrame()
    
#     # Mapeo a diccionario para Pandas
#     data = [dict(r._mapping) for r in query_results]
    
#     df = pd.DataFrame(data)
#     if "consumo_kwh" in df.columns:
#         df["consumo_kwh"] = pd.to_numeric(df["consumo_kwh"])
#     if "costo_total" in df.columns:
#         df["costo_total"] = pd.to_numeric(df["costo_total"])
        
#     return df


# # ============================================================
# #  FUNCIONES EXISTENTES (Single ID)
# # ============================================================

# def consumo_total_anual(db: Session, id_edificio: int) -> Dict:
#     stmt = (
#         select(
#             ConsumoHistorico.anio,
#             func.sum(ConsumoHistorico.consumo_kwh).label("total_kwh")
#         )
#         .where(ConsumoHistorico.edificio_id == id_edificio)
#         .group_by(ConsumoHistorico.anio)
#         .order_by(ConsumoHistorico.anio)
#     )
#     results = db.execute(stmt).all()
#     return {r.anio: float(r.total_kwh) for r in results}

# def consumo_mensual(db: Session, id_edificio: int, anio: int) -> Dict:
#     stmt = (
#         select(
#             ConsumoHistorico.mes,
#             ConsumoHistorico.consumo_kwh
#         )
#         .where(
#             ConsumoHistorico.edificio_id == id_edificio,
#             ConsumoHistorico.anio == anio
#         )
#         .order_by(ConsumoHistorico.mes)
#     )
#     results = db.execute(stmt).all()
#     return {m.mes: float(m.consumo_kwh) for m in results}

# def costo_total_anual(db: Session, id_edificio: int) -> Dict:
#     stmt = (
#         select(
#             ConsumoHistorico.anio,
#             func.sum(ConsumoHistorico.costo_total).label("costo_anual")
#         )
#         .where(ConsumoHistorico.edificio_id == id_edificio)
#         .group_by(ConsumoHistorico.anio)
#         .order_by(ConsumoHistorico.anio)
#     )
#     results = db.execute(stmt).all()
#     return {r.anio: float(r.costo_anual) for r in results}

# def consumo_promedio_anual(db: Session, id_edificio: int) -> Dict:
#     stmt = (
#         select(
#             ConsumoHistorico.anio,
#             func.avg(ConsumoHistorico.consumo_kwh).label("promedio_kwh")
#         )
#         .where(ConsumoHistorico.edificio_id == id_edificio)
#         .group_by(ConsumoHistorico.anio)
#         .order_by(ConsumoHistorico.anio)
#     )
#     results = db.execute(stmt).all()
#     return {r.anio: float(r.promedio_kwh) for r in results}

# def estacionalidad(db: Session, id_edificio: int) -> Dict:
#     stmt = (
#         select(
#             ConsumoHistorico.mes,
#             func.avg(ConsumoHistorico.consumo_kwh).label("promedio_mes")
#         )
#         .where(ConsumoHistorico.edificio_id == id_edificio)
#         .group_by(ConsumoHistorico.mes)
#         .order_by(ConsumoHistorico.mes)
#     )
#     results = db.execute(stmt).all()
#     return {r.mes: float(r.promedio_mes) for r in results}

# def ranking_meses(db: Session, id_edificio: int, top: int = 5) -> List[Dict]:
#     stmt = (
#         select(
#             ConsumoHistorico.anio,
#             ConsumoHistorico.mes,
#             ConsumoHistorico.consumo_kwh
#         )
#         .where(ConsumoHistorico.edificio_id == id_edificio)
#         .order_by(ConsumoHistorico.consumo_kwh.desc())
#         .limit(top)
#     )
#     results = db.execute(stmt).all()
#     return [
#         {
#             "anio": r.anio,
#             "mes": r.mes,
#             "consumo_kwh": float(r.consumo_kwh)
#         }
#         for r in results
#     ]

# def tendencia(db: Session, id_edificio: int, window: int = 3) -> List[Dict]:
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
#     registros = db.execute(stmt).all() 

#     df = _df_from_query(registros)
#     if df.empty:
#         return []

#     df["tendencia"] = df["consumo_kwh"].rolling(window=window, min_periods=1).mean()
#     df = df.where(pd.notnull(df), None)
    
#     return df.to_dict(orient="records")

# def anio_mayor_consumo(db: Session, id_edificio: int) -> Dict:
#     stmt = (
#         select(
#             ConsumoHistorico.anio,
#             func.sum(ConsumoHistorico.consumo_kwh).label("total")
#         )
#         .where(ConsumoHistorico.edificio_id == id_edificio)
#         .group_by(ConsumoHistorico.anio)
#         .order_by(func.sum(ConsumoHistorico.consumo_kwh).desc())
#     )
#     result = db.execute(stmt).first()

#     if not result:
#         return {}

#     return {"anio": result.anio, "total_kwh": float(result.total)}

# def potencial_ahorro(db: Session, id_edificio: int) -> Dict:
#     stmt = (
#         select(func.sum(ConsumoHistorico.consumo_kwh))
#         .where(ConsumoHistorico.edificio_id == id_edificio)
#     )
#     total = db.execute(stmt).scalar()

#     if not total:
#         return {}
    
#     total_float = float(total)
#     ahorro_10 = total_float * 0.10

#     return {
#         "consumo_actual": total_float,
#         "ahorro_potencial_kwh": ahorro_10,
#         "consumo_proyectado": total_float - ahorro_10,
#     }


# # ============================================================
# #   NUEVAS FUNCIONES PARA VISTA PÚBLICA (COMPARATIVAS)
# # ============================================================

# def resolver_ids_por_filtro(db: Session, tipo: str, ids_solicitados: List[int]) -> List[int]:
#     """
#     Convierte la selección del usuario (Sector/Dependencia) en una lista de IDs de edificios.
#     """
#     if tipo == "edificio":
#         return ids_solicitados  # Ya son edificios
    
#     if tipo == "dependencia":
#         # Buscar todos los edificios de estas dependencias
#         stmt = select(Edificio.id_edificio).where(Edificio.dependencia_id.in_(ids_solicitados))
#         return db.execute(stmt).scalars().all()
    
#     if tipo == "sector":
#         # Buscar dependencias del sector -> luego edificios
#         # JOIN Edificio -> Dependencia -> Sector
#         stmt = (
#             select(Edificio.id_edificio)
#             .join(Edificio.dependencia)
#             .where(Dependencia.sector_id.in_(ids_solicitados))
#         )
#         return db.execute(stmt).scalars().all()
    
#     return []


# def _generar_respuesta_comparativa(
#     db: Session, 
#     ids_edificios: List[int], 
#     datos_raw: List[Any], 
#     titulo: str,
#     es_costo: bool = False
# ) -> Dict:
#     """Helper interno para formatear respuestas de gráficas."""
#     stmt_nombres = select(Edificio.id_edificio, Edificio.nombre_edificio).where(Edificio.id_edificio.in_(ids_edificios))
#     nombres_map = {row.id_edificio: row.nombre_edificio for row in db.execute(stmt_nombres)}

#     # Eje X estándar de meses
#     eje_x = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    
#     series_dict = {id_ed: [0.0] * 12 for id_ed in ids_edificios}

#     for fila in datos_raw:
#         if 1 <= fila.mes <= 12:
#             valor = float(fila.costo_total) if es_costo else float(fila.consumo_kwh)
#             series_dict[fila.edificio_id][fila.mes - 1] = valor

#     lista_series = []
#     for id_ed, data_mensual in series_dict.items():
#         lista_series.append({
#             "nombre": nombres_map.get(id_ed, f"Edificio {id_ed}"),
#             "datos": data_mensual,
#             "color": None 
#         })

#     return {
#         "titulo": titulo,
#         "eje_x": eje_x,
#         "series": lista_series
#     }


# def comparativa_consumo_mensual(db: Session, ids_edificios: List[int], anio: int) -> Dict:
#     """
#     Genera la estructura para gráficas multi-serie (Chart.js).
#     Compara el consumo mensual de varios edificios en un año específico.
#     """
#     if not ids_edificios:
#         return {"titulo": "Sin datos", "eje_x": [], "series": []}

#     # Obtener datos de consumo
#     stmt = (
#         select(
#             ConsumoHistorico.edificio_id,
#             ConsumoHistorico.mes,
#             ConsumoHistorico.consumo_kwh
#         )
#         .where(
#             ConsumoHistorico.edificio_id.in_(ids_edificios),
#             ConsumoHistorico.anio == anio
#         )
#         .order_by(ConsumoHistorico.mes)
#     )
#     datos = db.execute(stmt).all()

#     return _generar_respuesta_comparativa(db, ids_edificios, datos, f"Comparativa Consumo (kWh) {anio}")


# def comparativa_costo_mensual(db: Session, ids_edificios: List[int], anio: int) -> Dict:
#     if not ids_edificios:
#         return {"titulo": "Sin datos", "eje_x": [], "series": []}

#     stmt = (
#         select(ConsumoHistorico.edificio_id, ConsumoHistorico.mes, ConsumoHistorico.costo_total)
#         .where(ConsumoHistorico.edificio_id.in_(ids_edificios), ConsumoHistorico.anio == anio)
#         .order_by(ConsumoHistorico.mes)
#     )
#     datos = db.execute(stmt).all()
#     return _generar_respuesta_comparativa(db, ids_edificios, datos, f"Comparativa Costos ($) {anio}", es_costo=True)


# def ranking_publico(db: Session, ids_edificios: List[int], anio: int) -> Dict:
#     """Top edificios con mayor consumo en el año seleccionado."""
#     if not ids_edificios:
#         return {"titulo": "Sin datos", "eje_x": [], "series": []}

#     # Top 10
#     stmt = (
#         select(
#             ConsumoHistorico.edificio_id,
#             func.sum(ConsumoHistorico.consumo_kwh).label("total")
#         )
#         .where(ConsumoHistorico.edificio_id.in_(ids_edificios), ConsumoHistorico.anio == anio)
#         .group_by(ConsumoHistorico.edificio_id)
#         .order_by(desc("total"))
#         .limit(10)
#     )
#     resultados = db.execute(stmt).all()
    
#     # Obtener nombres
#     ids_top = [r.edificio_id for r in resultados]
#     stmt_nombres = select(Edificio.id_edificio, Edificio.nombre_edificio).where(Edificio.id_edificio.in_(ids_top))
#     nombres_map = {row.id_edificio: row.nombre_edificio for row in db.execute(stmt_nombres)}

#     # Formato especial para gráfica de barras (Ranking)
#     # Eje X: Nombres de edificios
#     # Serie: Un solo conjunto de datos
#     eje_x = [nombres_map.get(r.edificio_id, str(r.edificio_id)) for r in resultados]
#     datos = [float(r.total) for r in resultados]

#     return {
#         "titulo": f"Top Consumo {anio}",
#         "eje_x": eje_x,
#         "series": [{
#             "nombre": "Total kWh",
#             "datos": datos,
#             "color": None
#         }]
#     }


# # ============================================================
# #   NUEVAS FUNCIONES: PRESUPUESTO VS GASTO
# # ============================================================

# def resolver_ids_dependencias_por_filtro(db: Session, tipo: str, ids_solicitados: List[int]) -> List[int]:
#     """
#     Similar a resolver edificios, pero devuelve IDs de DEPENDENCIAS.
#     Necesario porque el presupuesto está ligado a la Dependencia, no al edificio.
#     """
#     if tipo == "dependencia":
#         return ids_solicitados
    
#     if tipo == "sector":
#         # Traer todas las dependencias de estos sectores
#         stmt = select(Dependencia.id_dependencia).where(Dependencia.sector_id.in_(ids_solicitados))
#         return db.execute(stmt).scalars().all()
    
#     if tipo == "edificio":
#         # Traer las dependencias padres de estos edificios
#         stmt = select(Edificio.dependencia_id).where(Edificio.id_edificio.in_(ids_solicitados)).distinct()
#         return db.execute(stmt).scalars().all()
        
#     return []

# def analisis_presupuestal_trimestral(db: Session, ids_dependencias: List[int], anio: int) -> Dict:
#     """
#     Compara Trimestre a Trimestre: Dinero Asignado vs Dinero Gastado en Luz.
#     """
#     if not ids_dependencias:
#         return {"titulo": "Sin datos", "eje_x": [], "series": []}

#     # 1. Obtener Presupuesto (Agrupado por Trimestre)
#     stmt_presu = (
#         select(
#             Presupuesto.trimestre,
#             func.sum(Presupuesto.monto_asignado).label("total_asignado")
#         )
#         .where(
#             Presupuesto.dependencia_id.in_(ids_dependencias),
#             Presupuesto.anio == anio
#         )
#         .group_by(Presupuesto.trimestre)
#         .order_by(Presupuesto.trimestre)
#     )
#     data_presu = db.execute(stmt_presu).all()


#     stmt_edificios = select(Edificio.id_edificio).where(Edificio.dependencia_id.in_(ids_dependencias))
#     ids_edificios = db.execute(stmt_edificios).scalars().all()

#     stmt_gasto = (
#         select(
#             ConsumoHistorico.mes,
#             func.sum(ConsumoHistorico.costo_total).label("gasto_mes")
#         )
#         .where(
#             ConsumoHistorico.edificio_id.in_(ids_edificios),
#             ConsumoHistorico.anio == anio
#         )
#         .group_by(ConsumoHistorico.mes)
#     )
#     data_gasto = db.execute(stmt_gasto).all()

#     # 3. Procesar y Alinear Datos
#     trimestres = {1: {"presupuesto": 0.0, "gasto": 0.0}, 
#                   2: {"presupuesto": 0.0, "gasto": 0.0}, 
#                   3: {"presupuesto": 0.0, "gasto": 0.0}, 
#                   4: {"presupuesto": 0.0, "gasto": 0.0}}

#     # Llenar Presupuesto
#     for fila in data_presu:
#         if 1 <= fila.trimestre <= 4:
#             trimestres[fila.trimestre]["presupuesto"] = float(fila.total_asignado)

#     # Llenar Gasto (Sumando meses al trimestre correspondiente)
#     for fila in data_gasto:
#         trim = (fila.mes - 1) // 3 + 1  # Formula mágica: mes 1-3->1, 4-6->2...
#         if 1 <= trim <= 4:
#             trimestres[trim]["gasto"] += float(fila.gasto_mes)

#     # 4. Formatear para Gráfica
#     eje_x = ["Trimestre 1", "Trimestre 2", "Trimestre 3", "Trimestre 4"]
#     serie_presupuesto = [trimestres[t]["presupuesto"] for t in [1,2,3,4]]
#     serie_gasto = [trimestres[t]["gasto"] for t in [1,2,3,4]]

#     return {
#         "titulo": f"Presupuesto vs Gasto Energético {anio}",
#         "eje_x": eje_x,
#         "series": [
#             {
#                 "nombre": "Presupuesto Asignado",
#                 "datos": serie_presupuesto,
#                 "color": "#28a745" # Verde (Dinero disponible)
#             },
#             {
#                 "nombre": "Gasto en Energía",
#                 "datos": serie_gasto,
#                 "color": "#dc3545" # Rojo (Dinero que sale)
#             }
#         ]
#     }





# # ============================================================
# #  app/services/analisis_service.py
# #  Versión Final: Sintaxis 2.0 + Columnas Corregidas (edificio_id)
# #  + NUEVO: Lógica para comparativas y filtros masivos
# # ============================================================

# from sqlalchemy.orm import Session
# from sqlalchemy import func, select, desc
# from app.db.models import ConsumoHistorico, Edificio, Dependencia, Sector
# from typing import Dict, List, Any
# import pandas as pd

# def _df_from_query(query_results):
#     if not query_results:
#         return pd.DataFrame()
#     data = [dict(r._mapping) for r in query_results]
#     df = pd.DataFrame(data)
#     # Conversiones de tipo si son necesarias...
#     return df

# # ============================================================
# #  FUNCIONES EXISTENTES (Single ID - No Tocar)
# # ============================================================
# # 1) CONSUMO TOTAL ANUAL
# def consumo_total_anual(db: Session, id_edificio: int) -> Dict:
#     stmt = (
#         select(
#             ConsumoHistorico.anio,
#             func.sum(ConsumoHistorico.consumo_kwh).label("total_kwh")
#         )
#         .where(ConsumoHistorico.edificio_id == id_edificio)
#         .group_by(ConsumoHistorico.anio)
#         .order_by(ConsumoHistorico.anio)
#     )
#     results = db.execute(stmt).all()
#     return {r.anio: float(r.total_kwh) for r in results}

# # 2) CONSUMO MENSUAL
# def consumo_mensual(db: Session, id_edificio: int, anio: int) -> Dict:
#     stmt = (
#         select(
#             ConsumoHistorico.mes,
#             ConsumoHistorico.consumo_kwh
#         )
#         .where(
#             ConsumoHistorico.edificio_id == id_edificio,
#             ConsumoHistorico.anio == anio
#         )
#         .order_by(ConsumoHistorico.mes)
#     )
#     results = db.execute(stmt).all()
#     return {m.mes: float(m.consumo_kwh) for m in results}

# # 3) COSTO TOTAL ANUAL
# def costo_total_anual(db: Session, id_edificio: int) -> Dict:
#     stmt = (
#         select(
#             ConsumoHistorico.anio,
#             func.sum(ConsumoHistorico.costo_total).label("costo_anual")
#         )
#         .where(ConsumoHistorico.edificio_id == id_edificio)
#         .group_by(ConsumoHistorico.anio)
#         .order_by(ConsumoHistorico.anio)
#     )
#     results = db.execute(stmt).all()
#     return {r.anio: float(r.costo_anual) for r in results}

# # 4) CONSUMO PROMEDIO ANUAL
# def consumo_promedio_anual(db: Session, id_edificio: int) -> Dict:
#     stmt = (
#         select(
#             ConsumoHistorico.anio,
#             func.avg(ConsumoHistorico.consumo_kwh).label("promedio_kwh")
#         )
#         .where(ConsumoHistorico.edificio_id == id_edificio)
#         .group_by(ConsumoHistorico.anio)
#         .order_by(ConsumoHistorico.anio)
#     )
#     results = db.execute(stmt).all()
#     return {r.anio: float(r.promedio_kwh) for r in results}

# # 5) ESTACIONALIDAD
# def estacionalidad(db: Session, id_edificio: int) -> Dict:
#     stmt = (
#         select(
#             ConsumoHistorico.mes,
#             func.avg(ConsumoHistorico.consumo_kwh).label("promedio_mes")
#         )
#         .where(ConsumoHistorico.edificio_id == id_edificio)
#         .group_by(ConsumoHistorico.mes)
#         .order_by(ConsumoHistorico.mes)
#     )
#     results = db.execute(stmt).all()
#     return {r.mes: float(r.promedio_mes) for r in results}

# # 6) RANKING MESES
# def ranking_meses(db: Session, id_edificio: int, top: int = 5) -> List[Dict]:
#     stmt = (
#         select(
#             ConsumoHistorico.anio,
#             ConsumoHistorico.mes,
#             ConsumoHistorico.consumo_kwh
#         )
#         .where(ConsumoHistorico.edificio_id == id_edificio)
#         .order_by(ConsumoHistorico.consumo_kwh.desc())
#         .limit(top)
#     )
#     results = db.execute(stmt).all()
#     return [{"anio": r.anio, "mes": r.mes, "consumo_kwh": float(r.consumo_kwh)} for r in results]

# # 7) TENDENCIA
# def tendencia(db: Session, id_edificio: int, window: int = 3) -> List[Dict]:
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
#     registros = db.execute(stmt).all()
#     df = _df_from_query(registros)
#     if df.empty:
#         return []
#     df["tendencia"] = df["consumo_kwh"].rolling(window=window, min_periods=1).mean()
#     df = df.where(pd.notnull(df), None)
#     return df.to_dict(orient="records")

# # 8) AÑO MAYOR CONSUMO
# def anio_mayor_consumo(db: Session, id_edificio: int) -> Dict:
#     stmt = (
#         select(
#             ConsumoHistorico.anio,
#             func.sum(ConsumoHistorico.consumo_kwh).label("total")
#         )
#         .where(ConsumoHistorico.edificio_id == id_edificio)
#         .group_by(ConsumoHistorico.anio)
#         .order_by(func.sum(ConsumoHistorico.consumo_kwh).desc())
#     )
#     result = db.execute(stmt).first()
#     if not result:
#         return {}
#     return {"anio": result.anio, "total_kwh": float(result.total)}

# # 9) POTENCIAL AHORRO
# def potencial_ahorro(db: Session, id_edificio: int) -> Dict:
#     stmt = (
#         select(func.sum(ConsumoHistorico.consumo_kwh))
#         .where(ConsumoHistorico.edificio_id == id_edificio)
#     )
#     total = db.execute(stmt).scalar()
#     if not total:
#         return {}
#     total_float = float(total)
#     ahorro_10 = total_float * 0.10
#     return {
#         "consumo_actual": total_float,
#         "ahorro_potencial_kwh": ahorro_10,
#         "consumo_proyectado": total_float - ahorro_10,
#     }


# # ============================================================
# #  🚀 NUEVAS FUNCIONES PARA VISTA PÚBLICA (COMPARATIVAS)
# # ============================================================

# def resolver_ids_por_filtro(db: Session, tipo: str, ids_solicitados: List[int]) -> List[int]:
#     """
#     Convierte la selección del usuario (Sector/Dependencia) en una lista de IDs de edificios.
#     """
#     if tipo == "edificio":
#         return ids_solicitados  # Ya son edificios
    
#     if tipo == "dependencia":
#         # Buscar todos los edificios de estas dependencias
#         stmt = select(Edificio.id_edificio).where(Edificio.dependencia_id.in_(ids_solicitados))
#         return db.execute(stmt).scalars().all()
    
#     if tipo == "sector":
#         # Buscar dependencias del sector -> luego edificios
#         # JOIN Edificio -> Dependencia -> Sector
#         stmt = (
#             select(Edificio.id_edificio)
#             .join(Edificio.dependencia)
#             .where(Dependencia.sector_id.in_(ids_solicitados))
#         )
#         return db.execute(stmt).scalars().all()
    
#     return []


# def comparativa_consumo_mensual(db: Session, ids_edificios: List[int], anio: int) -> Dict:
#     """
#     Genera la estructura para gráficas multi-serie (Chart.js).
#     Compara el consumo mensual de varios edificios en un año específico.
#     """
#     if not ids_edificios:
#         return {"titulo": "Sin datos", "eje_x": [], "series": []}

#     # 1. Obtener nombres de los edificios para las leyendas
#     stmt_nombres = select(Edificio.id_edificio, Edificio.nombre_edificio).where(Edificio.id_edificio.in_(ids_edificios))
#     nombres_map = {row.id_edificio: row.nombre_edificio for row in db.execute(stmt_nombres)}

#     # 2. Obtener datos de consumo
#     stmt_datos = (
#         select(
#             ConsumoHistorico.edificio_id,
#             ConsumoHistorico.mes,
#             ConsumoHistorico.consumo_kwh
#         )
#         .where(
#             ConsumoHistorico.edificio_id.in_(ids_edificios),
#             ConsumoHistorico.anio == anio
#         )
#         .order_by(ConsumoHistorico.mes)
#     )
#     datos_raw = db.execute(stmt_datos).all()

#     # 3. Estructurar datos
#     # Eje X siempre son los 12 meses
#     eje_x = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    
#     # Inicializar series con 0s
#     series_dict = {
#         id_ed: [0.0] * 12 for id_ed in ids_edificios
#     }

#     # Llenar con datos reales
#     for fila in datos_raw:
#         # mes 1 -> índice 0
#         if 1 <= fila.mes <= 12:
#             series_dict[fila.edificio_id][fila.mes - 1] = float(fila.consumo_kwh)

#     # 4. Formatear respuesta final
#     lista_series = []
#     for id_ed, data_mensual in series_dict.items():
#         lista_series.append({
#             "nombre": nombres_map.get(id_ed, f"Edificio {id_ed}"),
#             "datos": data_mensual,
#             "color": None # El frontend puede asignar colores aleatorios
#         })

#     return {
#         "titulo": f"Comparativa de Consumo {anio}",
#         "eje_x": eje_x,
#         "series": lista_series
#     }