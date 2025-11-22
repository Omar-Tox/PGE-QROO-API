# ============================================================
#  app/services/analisis_service.py
#  Versión Final: Lógica completa para análisis energético y financiero
#  Incluye soporte para Comparativas Públicas y Dashboard Privado
# ============================================================

from sqlalchemy.orm import Session
from sqlalchemy import func, select, desc
from app.db.models import ConsumoHistorico, Edificio, Dependencia, Sector, Presupuesto, User, usuario_dependencia_roles
from typing import Dict, List, Any, Optional
import pandas as pd


# ============================================================
#  UTILERÍA INTERNA
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

def _obtener_nombres_dependencias(db: Session, ids_edificios: List[int]) -> List[str]:
    """Obtiene los nombres únicos de las dependencias asociadas a una lista de edificios."""
    if not ids_edificios:
        return []
    
    stmt = (
        select(Dependencia.nombre_dependencia)
        .join(Edificio, Edificio.dependencia_id == Dependencia.id_dependencia)
        .where(Edificio.id_edificio.in_(ids_edificios))
        .distinct()
    )
    return list(db.execute(stmt).scalars().all())

def _generar_respuesta_comparativa(
    db: Session, 
    ids_edificios: List[int], 
    datos_raw: List[Any], 
    titulo: str,
    es_costo: bool = False
) -> Dict:
    """Helper interno para formatear respuestas de gráficas."""
    # Obtener nombres de edificios para las series
    stmt_nombres = select(Edificio.id_edificio, Edificio.nombre_edificio).where(Edificio.id_edificio.in_(ids_edificios))
    nombres_map = {row.id_edificio: row.nombre_edificio for row in db.execute(stmt_nombres)}
    
    # Obtener contexto (Dependencias)
    deps_names = _obtener_nombres_dependencias(db, ids_edificios)

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
        "series": lista_series,
        "dependencias_involucradas": deps_names
    }


# ============================================================
#  UTILERÍA DE USUARIO (DASHBOARD PRIVADO)
# ============================================================

def obtener_edificios_usuario(db: Session, user_id: int, filtro_dependencia_id: Optional[int] = None) -> List[int]:
    """
    Busca todos los edificios a los que el usuario tiene acceso.
    Si se envía 'filtro_dependencia_id', se valida que el usuario tenga acceso a ella
    y se retornan solo los edificios de esa dependencia.
    """
    # 1. Obtener TODAS las dependencias del usuario desde la tabla pivote
    stmt_deps = select(usuario_dependencia_roles.c.dependencia_id).where(
        usuario_dependencia_roles.c.usuario_id == user_id
    )
    ids_deps_permitidos = db.execute(stmt_deps).scalars().all()

    if not ids_deps_permitidos:
        return [] # Usuario sin dependencias asignadas

    # 2. Aplicar lógica de filtrado seguro
    ids_a_consultar = []
    
    if filtro_dependencia_id:
        # VALIDACIÓN DE SEGURIDAD:
        # Solo permitimos filtrar si el ID solicitado está dentro de los permitidos del usuario.
        if filtro_dependencia_id in ids_deps_permitidos:
            ids_a_consultar = [filtro_dependencia_id]
        else:
            # Si pide una dependencia que no es suya, retornamos lista vacía (acceso denegado implícito)
            return []
    else:
        # Si no hay filtro, usamos todas las dependencias permitidas
        ids_a_consultar = list(ids_deps_permitidos)

    # 3. Obtener edificios
    stmt_edificios = select(Edificio.id_edificio).where(
        Edificio.dependencia_id.in_(ids_a_consultar)
    )
    ids_edificios = db.execute(stmt_edificios).scalars().all()
    
    return list(ids_edificios)


# ============================================================
#  FUNCIONES EXISTENTES (Single ID) - Mantenidas por compatibilidad
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
#  FUNCIONES VISTA PÚBLICA (COMPARATIVAS)
# ============================================================

def resolver_ids_por_filtro(db: Session, tipo: str, ids_solicitados: List[int]) -> List[int]:
    """
    Convierte la selección del usuario (Sector/Dependencia) en una lista de IDs de edificios.
    """
    if tipo == "edificio":
        return ids_solicitados
    
    if tipo == "dependencia":
        stmt = select(Edificio.id_edificio).where(Edificio.dependencia_id.in_(ids_solicitados))
        return db.execute(stmt).scalars().all()
    
    if tipo == "sector":
        stmt = (
            select(Edificio.id_edificio)
            .join(Edificio.dependencia)
            .where(Dependencia.sector_id.in_(ids_solicitados))
        )
        return db.execute(stmt).scalars().all()
    
    return []


def comparativa_consumo_mensual(db: Session, ids_edificios: List[int], anio: int) -> Dict:
    """Genera la estructura para gráficas multi-serie (Chart.js) de consumo kWh."""
    if not ids_edificios:
        return {"titulo": "Sin datos", "eje_x": [], "series": [], "dependencias_involucradas": []}

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
    """Genera la estructura para gráficas multi-serie (Chart.js) de costos ($)."""
    if not ids_edificios:
        return {"titulo": "Sin datos", "eje_x": [], "series": [], "dependencias_involucradas": []}

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
        return {"titulo": "Sin datos", "eje_x": [], "series": [], "dependencias_involucradas": []}

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
    
    # Contexto
    deps_names = _obtener_nombres_dependencias(db, ids_edificios)

    eje_x = [nombres_map.get(r.edificio_id, str(r.edificio_id)) for r in resultados]
    datos = [float(r.total) for r in resultados]

    return {
        "titulo": f"Top Consumo {anio}",
        "eje_x": eje_x,
        "series": [{"nombre": "Total kWh", "datos": datos, "color": None}],
        "dependencias_involucradas": deps_names
    }


# ============================================================
#  FUNCIONES PRESUPUESTO VS GASTO
# ============================================================

def resolver_ids_dependencias_por_filtro(db: Session, tipo: str, ids_solicitados: List[int]) -> List[int]:
    """
    Devuelve IDs de DEPENDENCIAS basados en el filtro.
    """
    if tipo == "dependencia":
        return ids_solicitados
    
    if tipo == "sector":
        stmt = select(Dependencia.id_dependencia).where(Dependencia.sector_id.in_(ids_solicitados))
        return db.execute(stmt).scalars().all()
    
    if tipo == "edificio":
        stmt = select(Edificio.dependencia_id).where(Edificio.id_edificio.in_(ids_solicitados)).distinct()
        return db.execute(stmt).scalars().all()
        
    return []

def analisis_presupuestal_trimestral(db: Session, ids_dependencias: List[int], anio: int) -> Dict:
    """
    Compara Trimestre a Trimestre: Dinero Asignado (Dependencia) vs Gasto Real (Suma de Edificios).
    """
    if not ids_dependencias:
        return {"titulo": "Sin datos", "eje_x": [], "series": [], "dependencias_involucradas": []}

    # Contexto
    stmt_names = select(Dependencia.nombre_dependencia).where(Dependencia.id_dependencia.in_(ids_dependencias))
    deps_names = list(db.execute(stmt_names).scalars().all())

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
    stmt_gasto = (
        select(
            ConsumoHistorico.mes,
            func.sum(ConsumoHistorico.costo_total).label("gasto_mes")
        )
        .join(ConsumoHistorico.edificio)
        .where(
            Edificio.dependencia_id.in_(ids_dependencias),
            ConsumoHistorico.anio == anio
        )
        .group_by(ConsumoHistorico.mes)
    )
    data_gasto = db.execute(stmt_gasto).all()

    # 3. Procesar y Alinear Datos
    trimestres = {
        1: {"presupuesto": 0.0, "gasto": 0.0}, 
        2: {"presupuesto": 0.0, "gasto": 0.0}, 
        3: {"presupuesto": 0.0, "gasto": 0.0}, 
        4: {"presupuesto": 0.0, "gasto": 0.0}
    }

    for fila in data_presu:
        if 1 <= fila.trimestre <= 4:
            trimestres[fila.trimestre]["presupuesto"] = float(fila.total_asignado)

    for fila in data_gasto:
        trim = (fila.mes - 1) // 3 + 1 
        if 1 <= trim <= 4:
            trimestres[trim]["gasto"] += float(fila.gasto_mes)

    eje_x = ["Trimestre 1", "Trimestre 2", "Trimestre 3", "Trimestre 4"]
    serie_presupuesto = [trimestres[t]["presupuesto"] for t in [1,2,3,4]]
    serie_gasto = [trimestres[t]["gasto"] for t in [1,2,3,4]]

    return {
        "titulo": f"Presupuesto vs Gasto Energético {anio}",
        "eje_x": eje_x,
        "series": [
            {"nombre": "Presupuesto Asignado", "datos": serie_presupuesto, "color": "#28a745"},
            {"nombre": "Gasto en Energía", "datos": serie_gasto, "color": "#dc3545"}
        ],
        "dependencias_involucradas": deps_names
    }


# ============================================================
#  CÁLCULOS AGREGADOS (DASHBOARD PRIVADO - ACTUALIZADOS)
# ============================================================

def kpis_anuales(db: Session, ids_edificios: List[int], anio: int) -> Dict:
    """
    Calcula métricas financieras reales: Gasto, Presupuesto y Balance.
    """
    if not ids_edificios:
        return {
            "anio": anio, "total_kwh": 0, "promedio_kwh": 0,
            "costo_total_energia": 0, "presupuesto_asignado": 0,
            "balance_financiero": 0, "estado_presupuestal": "Sin datos",
            "dependencias_involucradas": []
        }

    # 1. Consumo y Gasto
    stmt_consumo = (
        select(
            func.sum(ConsumoHistorico.consumo_kwh).label("total_kwh"),
            func.sum(ConsumoHistorico.costo_total).label("total_costo"),
            func.avg(ConsumoHistorico.consumo_kwh).label("promedio_kwh")
        )
        .where(
            ConsumoHistorico.edificio_id.in_(ids_edificios),
            ConsumoHistorico.anio == anio
        )
    )
    res_consumo = db.execute(stmt_consumo).first()
    
    gasto_energia = float(res_consumo.total_costo or 0)
    total_kwh = float(res_consumo.total_kwh or 0)
    promedio_kwh = float(res_consumo.promedio_kwh or 0)

    # 2. Identificar Dependencias (para presupuesto y contexto)
    stmt_deps = select(Edificio.dependencia_id).where(Edificio.id_edificio.in_(ids_edificios)).distinct()
    ids_dependencias = list(db.execute(stmt_deps).scalars().all())

    presupuesto_total = 0.0
    nombres_dependencias = []

    if ids_dependencias:
        stmt_presupuesto = (
            select(func.sum(Presupuesto.monto_asignado))
            .where(
                Presupuesto.dependencia_id.in_(ids_dependencias),
                Presupuesto.anio == anio
            )
        )
        presupuesto_total = float(db.execute(stmt_presupuesto).scalar() or 0)

        stmt_nombres = select(Dependencia.nombre_dependencia).where(Dependencia.id_dependencia.in_(ids_dependencias))
        nombres_dependencias = list(db.execute(stmt_nombres).scalars().all())

    balance = presupuesto_total - gasto_energia
    estado = "Superávit" if balance >= 0 else "Déficit (Sobregiro)"

    return {
        "anio": anio,
        "total_kwh": total_kwh,
        "promedio_kwh": promedio_kwh,
        "costo_total_energia": gasto_energia,
        "presupuesto_asignado": presupuesto_total,
        "balance_financiero": balance,
        "estado_presupuestal": estado,
        "dependencias_involucradas": nombres_dependencias
    }


def evolucion_mensual_agregada(db: Session, ids_edificios: List[int], anio: int) -> Dict:
    """Suma de consumo y costo por mes (Ene-Dic) de TODOS los edificios."""
    if not ids_edificios:
        return {"anio": anio, "eje_x": [], "serie_consumo_kwh": [], "serie_costo": [], "dependencias_involucradas": []}

    stmt = (
        select(
            ConsumoHistorico.mes,
            func.sum(ConsumoHistorico.consumo_kwh).label("kwh"),
            func.sum(ConsumoHistorico.costo_total).label("dinero")
        )
        .where(
            ConsumoHistorico.edificio_id.in_(ids_edificios),
            ConsumoHistorico.anio == anio
        )
        .group_by(ConsumoHistorico.mes)
        .order_by(ConsumoHistorico.mes)
    )
    resultados = db.execute(stmt).all()
    
    # Contexto
    deps_names = _obtener_nombres_dependencias(db, ids_edificios)

    eje_x = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    data_kwh = [0.0] * 12
    data_costo = [0.0] * 12

    for r in resultados:
        if 1 <= r.mes <= 12:
            data_kwh[r.mes - 1] = float(r.kwh)
            data_costo[r.mes - 1] = float(r.dinero)

    return {
        "anio": anio,
        "eje_x": eje_x,
        "serie_consumo_kwh": data_kwh,
        "serie_costo": data_costo,
        "dependencias_involucradas": deps_names
    }


def tendencia_agregada(db: Session, ids_edificios: List[int], window: int = 3) -> Dict:
    if not ids_edificios: return {"historico": [], "dependencias_involucradas": []}
    
    # Contexto
    deps_names = _obtener_nombres_dependencias(db, ids_edificios)

    stmt = (
        select(
            ConsumoHistorico.anio,
            ConsumoHistorico.mes,
            func.sum(ConsumoHistorico.consumo_kwh).label("consumo_kwh")
        )
        .where(ConsumoHistorico.edificio_id.in_(ids_edificios))
        .group_by(ConsumoHistorico.anio, ConsumoHistorico.mes)
        .order_by(ConsumoHistorico.anio, ConsumoHistorico.mes)
    )
    resultados = db.execute(stmt).all()
    
    data = [dict(r._mapping) for r in resultados]
    df = pd.DataFrame(data)
    
    if df.empty:
        return {"historico": [], "dependencias_involucradas": deps_names}

    if "consumo_kwh" in df.columns:
        df["consumo_kwh"] = pd.to_numeric(df["consumo_kwh"])

    df["tendencia"] = df["consumo_kwh"].rolling(window=window, min_periods=1).mean()
    df = df.where(pd.notnull(df), None)

    return {
        "historico": df.to_dict(orient="records"),
        "dependencias_involucradas": deps_names
    }


def ranking_interno_usuario(db: Session, ids_edificios: List[int], anio: int) -> Dict:
    if not ids_edificios: return {"nombres": [], "valores": [], "dependencias_involucradas": []}
    
    # Contexto
    deps_names = _obtener_nombres_dependencias(db, ids_edificios)

    stmt = (
        select(
            Edificio.nombre_edificio,
            func.sum(ConsumoHistorico.consumo_kwh).label("total")
        )
        .join(Edificio.consumos)
        .where(
            ConsumoHistorico.edificio_id.in_(ids_edificios),
            ConsumoHistorico.anio == anio
        )
        .group_by(Edificio.nombre_edificio)
        .order_by(desc("total"))
        .limit(10)
    )
    resultados = db.execute(stmt).all()

    return {
        "nombres": [r.nombre_edificio for r in resultados],
        "valores": [float(r.total) for r in resultados],
        "dependencias_involucradas": deps_names
    }
# # ============================================================
# #  app/services/analisis_service.py
# #  Versión Final: Soporte para filtrado por dependencia en dashboard privado
# # ============================================================

# from sqlalchemy.orm import Session
# from sqlalchemy import func, select, desc
# from app.db.models import ConsumoHistorico, Edificio, Dependencia, Sector, Presupuesto, User, usuario_dependencia_roles
# from typing import Dict, List, Any, Optional
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
# #  UTILERÍA INTERNA
# # ============================================================

# def _obtener_nombres_dependencias(db: Session, ids_edificios: List[int]) -> List[str]:
#     """Obtiene los nombres únicos de las dependencias asociadas a una lista de edificios."""
#     if not ids_edificios:
#         return []
    
#     stmt = (
#         select(Dependencia.nombre_dependencia)
#         .join(Edificio, Edificio.dependencia_id == Dependencia.id_dependencia)
#         .where(Edificio.id_edificio.in_(ids_edificios))
#         .distinct()
#     )
#     return list(db.execute(stmt).scalars().all())

# # ============================================================
# #  UTILERÍA DE USUARIO (ACTUALIZADO CON FILTRO OPCIONAL)
# # ============================================================

# def obtener_edificios_usuario(db: Session, user_id: int, filtro_dependencia_id: Optional[int] = None) -> List[int]:
#     """
#     Busca todos los edificios a los que el usuario tiene acceso.
#     Si se envía 'filtro_dependencia_id', se valida que el usuario tenga acceso a ella
#     y se retornan solo los edificios de esa dependencia.
#     """
#     # 1. Obtener TODAS las dependencias del usuario desde la tabla pivote
#     stmt_deps = select(usuario_dependencia_roles.c.dependencia_id).where(
#         usuario_dependencia_roles.c.usuario_id == user_id
#     )
#     ids_deps_permitidos = db.execute(stmt_deps).scalars().all()

#     if not ids_deps_permitidos:
#         return [] # Usuario sin dependencias asignadas

#     # 2. Aplicar lógica de filtrado seguro
#     ids_a_consultar = []
    
#     if filtro_dependencia_id:
#         # VALIDACIÓN DE SEGURIDAD:
#         # Solo permitimos filtrar si el ID solicitado está dentro de los permitidos del usuario.
#         if filtro_dependencia_id in ids_deps_permitidos:
#             ids_a_consultar = [filtro_dependencia_id]
#         else:
#             # Si pide una dependencia que no es suya, retornamos lista vacía (acceso denegado implícito)
#             return []
#     else:
#         # Si no hay filtro, usamos todas las dependencias permitidas
#         ids_a_consultar = list(ids_deps_permitidos)

#     # 3. Obtener edificios
#     stmt_edificios = select(Edificio.id_edificio).where(
#         Edificio.dependencia_id.in_(ids_a_consultar)
#     )
#     ids_edificios = db.execute(stmt_edificios).scalars().all()
    
#     return list(ids_edificios)


# # ============================================================
# #  FUNCIONES EXISTENTES (Single ID) - Se mantienen igual
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
#     return [{"anio": r.anio, "mes": r.mes, "consumo_kwh": float(r.consumo_kwh)} for r in results]

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
# #  FUNCIONES VISTA PÚBLICA (COMPARATIVAS) - Se mantienen igual
# # ============================================================

# def resolver_ids_por_filtro(db: Session, tipo: str, ids_solicitados: List[int]) -> List[int]:
#     if tipo == "edificio":
#         return ids_solicitados
#     if tipo == "dependencia":
#         stmt = select(Edificio.id_edificio).where(Edificio.dependencia_id.in_(ids_solicitados))
#         return db.execute(stmt).scalars().all()
#     if tipo == "sector":
#         stmt = (
#             select(Edificio.id_edificio)
#             .join(Edificio.dependencia)
#             .where(Dependencia.sector_id.in_(ids_solicitados))
#         )
#         return db.execute(stmt).scalars().all()
#     return []

# def _generar_respuesta_comparativa(db: Session, ids_edificios: List[int], datos_raw: List[Any], titulo: str, es_costo: bool = False) -> Dict:
#     stmt_nombres = select(Edificio.id_edificio, Edificio.nombre_edificio).where(Edificio.id_edificio.in_(ids_edificios))
#     nombres_map = {row.id_edificio: row.nombre_edificio for row in db.execute(stmt_nombres)}
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
#     return {"titulo": titulo, "eje_x": eje_x, "series": lista_series}

# def comparativa_consumo_mensual(db: Session, ids_edificios: List[int], anio: int) -> Dict:
#     if not ids_edificios:
#         return {"titulo": "Sin datos", "eje_x": [], "series": []}
#     stmt = (
#         select(ConsumoHistorico.edificio_id, ConsumoHistorico.mes, ConsumoHistorico.consumo_kwh)
#         .where(ConsumoHistorico.edificio_id.in_(ids_edificios), ConsumoHistorico.anio == anio)
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
#     if not ids_edificios:
#         return {"titulo": "Sin datos", "eje_x": [], "series": []}
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
#     ids_top = [r.edificio_id for r in resultados]
#     stmt_nombres = select(Edificio.id_edificio, Edificio.nombre_edificio).where(Edificio.id_edificio.in_(ids_top))
#     nombres_map = {row.id_edificio: row.nombre_edificio for row in db.execute(stmt_nombres)}
#     eje_x = [nombres_map.get(r.edificio_id, str(r.edificio_id)) for r in resultados]
#     datos = [float(r.total) for r in resultados]
#     return {
#         "titulo": f"Top Consumo {anio}",
#         "eje_x": eje_x,
#         "series": [{"nombre": "Total kWh", "datos": datos, "color": None}]
#     }

# # ============================================================
# #  FUNCIONES PRESUPUESTO VS GASTO
# # ============================================================
# def resolver_ids_dependencias_por_filtro(db: Session, tipo: str, ids_solicitados: List[int]) -> List[int]:
#     if tipo == "dependencia": return ids_solicitados
#     if tipo == "sector":
#         stmt = select(Dependencia.id_dependencia).where(Dependencia.sector_id.in_(ids_solicitados))
#         return db.execute(stmt).scalars().all()
#     if tipo == "edificio":
#         stmt = select(Edificio.dependencia_id).where(Edificio.id_edificio.in_(ids_solicitados)).distinct()
#         return db.execute(stmt).scalars().all()
#     return []

# def analisis_presupuestal_trimestral(db: Session, ids_dependencias: List[int], anio: int) -> Dict:
#     if not ids_dependencias: return {"titulo": "Sin datos", "eje_x": [], "series": []}
#     stmt_presu = (
#         select(Presupuesto.trimestre, func.sum(Presupuesto.monto_asignado).label("total_asignado"))
#         .where(Presupuesto.dependencia_id.in_(ids_dependencias), Presupuesto.anio == anio)
#         .group_by(Presupuesto.trimestre).order_by(Presupuesto.trimestre)
#     )
#     data_presu = db.execute(stmt_presu).all()
#     stmt_gasto = (
#         select(ConsumoHistorico.mes, func.sum(ConsumoHistorico.costo_total).label("gasto_mes"))
#         .join(ConsumoHistorico.edificio)
#         .where(Edificio.dependencia_id.in_(ids_dependencias), ConsumoHistorico.anio == anio)
#         .group_by(ConsumoHistorico.mes)
#     )
#     data_gasto = db.execute(stmt_gasto).all()
#     trimestres = {1: {"presupuesto": 0.0, "gasto": 0.0}, 2: {"presupuesto": 0.0, "gasto": 0.0}, 3: {"presupuesto": 0.0, "gasto": 0.0}, 4: {"presupuesto": 0.0, "gasto": 0.0}}
#     for fila in data_presu:
#         if 1 <= fila.trimestre <= 4: trimestres[fila.trimestre]["presupuesto"] = float(fila.total_asignado)
#     for fila in data_gasto:
#         trim = (fila.mes - 1) // 3 + 1
#         if 1 <= trim <= 4: trimestres[trim]["gasto"] += float(fila.gasto_mes)
#     eje_x = ["Trimestre 1", "Trimestre 2", "Trimestre 3", "Trimestre 4"]
#     serie_presupuesto = [trimestres[t]["presupuesto"] for t in [1,2,3,4]]
#     serie_gasto = [trimestres[t]["gasto"] for t in [1,2,3,4]]
#     return {
#         "titulo": f"Presupuesto vs Gasto Energético {anio}",
#         "eje_x": eje_x,
#         "series": [
#             {"nombre": "Presupuesto Asignado", "datos": serie_presupuesto, "color": "#28a745"},
#             {"nombre": "Gasto en Energía", "datos": serie_gasto, "color": "#dc3545"}
#         ]
#     }


# # ============================================================
# #  CÁLCULOS AGREGADOS (DASHBOARD PRIVADO)
# # ============================================================


# def kpis_anuales(db: Session, ids_edificios: List[int], anio: int) -> Dict:
#     """
#     Calcula métricas financieras reales:
#     1. Gasto Total de los edificios seleccionados.
#     2. Presupuesto Total de las dependencias a las que pertenecen esos edificios.
#     3. Balance (Presupuesto - Gasto).
#     """
#     if not ids_edificios:
#         return {
#             "anio": anio,
#             "total_kwh": 0, "promedio_kwh": 0,
#             "costo_total_energia": 0, "presupuesto_asignado": 0,
#             "balance_financiero": 0, "estado_presupuestal": "Sin datos",
#             "dependencias_involucradas": []
#         }

#     # 1. Calcular Consumo y Gasto Real (Tabla ConsumoHistorico)
#     stmt_consumo = (
#         select(
#             func.sum(ConsumoHistorico.consumo_kwh).label("total_kwh"),
#             func.sum(ConsumoHistorico.costo_total).label("total_costo"),
#             func.avg(ConsumoHistorico.consumo_kwh).label("promedio_kwh")
#         )
#         .where(
#             ConsumoHistorico.edificio_id.in_(ids_edificios),
#             ConsumoHistorico.anio == anio
#         )
#     )
#     res_consumo = db.execute(stmt_consumo).first()
    
#     gasto_energia = float(res_consumo.total_costo or 0)
#     total_kwh = float(res_consumo.total_kwh or 0)
#     promedio_kwh = float(res_consumo.promedio_kwh or 0)

#     # 2. Identificar Dependencias Involucradas (Para buscar su presupuesto y nombres)
#     # Buscamos los IDs de dependencia únicos asociados a la lista de edificios
#     stmt_deps = select(Edificio.dependencia_id).where(Edificio.id_edificio.in_(ids_edificios)).distinct()
#     ids_dependencias = list(db.execute(stmt_deps).scalars().all())

#     presupuesto_total = 0.0
#     nombres_dependencias = []

#     if ids_dependencias:
#         # 3. Obtener Presupuesto de esas Dependencias
#         stmt_presupuesto = (
#             select(func.sum(Presupuesto.monto_asignado))
#             .where(
#                 Presupuesto.dependencia_id.in_(ids_dependencias),
#                 Presupuesto.anio == anio
#             )
#         )
#         presupuesto_total = float(db.execute(stmt_presupuesto).scalar() or 0)

#         # 4. Obtener Nombres para el Contexto
#         stmt_nombres = select(Dependencia.nombre_dependencia).where(Dependencia.id_dependencia.in_(ids_dependencias))
#         nombres_dependencias = list(db.execute(stmt_nombres).scalars().all())

#     # 5. Cálculo Final
#     balance = presupuesto_total - gasto_energia
#     estado = "Superávit" if balance >= 0 else "Déficit (Sobregiro)"

#     return {
#         "anio": anio,
#         "total_kwh": total_kwh,
#         "promedio_kwh": promedio_kwh,
#         "costo_total_energia": gasto_energia,
#         "presupuesto_asignado": presupuesto_total,
#         "balance_financiero": balance,
#         "estado_presupuestal": estado,
#         "dependencias_involucradas": nombres_dependencias
#     }

# def evolucion_mensual_agregada(db: Session, ids_edificios: List[int], anio: int) -> Dict:
#     """Suma de consumo y costo por mes (Ene-Dic) de TODOS los edificios."""
#     if not ids_edificios:
#         return {"eje_x": [], "consumo": [], "costo": []}

#     stmt = (
#         select(
#             ConsumoHistorico.mes,
#             func.sum(ConsumoHistorico.consumo_kwh).label("kwh"),
#             func.sum(ConsumoHistorico.costo_total).label("dinero")
#         )
#         .where(
#             ConsumoHistorico.edificio_id.in_(ids_edificios),
#             ConsumoHistorico.anio == anio
#         )
#         .group_by(ConsumoHistorico.mes)
#         .order_by(ConsumoHistorico.mes)
#     )
#     resultados = db.execute(stmt).all()
#     eje_x = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
#     data_kwh = [0.0] * 12
#     data_costo = [0.0] * 12
#     for r in resultados:
#         if 1 <= r.mes <= 12:
#             data_kwh[r.mes - 1] = float(r.kwh)
#             data_costo[r.mes - 1] = float(r.dinero)
#     return {"anio": anio, "eje_x": eje_x, "serie_consumo_kwh": data_kwh, "serie_costo": data_costo}

# def tendencia_agregada(db: Session, ids_edificios: List[int], window: int = 3) -> List[Dict]:
#     if not ids_edificios: return []
#     stmt = (
#         select(
#             ConsumoHistorico.anio,
#             ConsumoHistorico.mes,
#             func.sum(ConsumoHistorico.consumo_kwh).label("consumo_kwh")
#         )
#         .where(ConsumoHistorico.edificio_id.in_(ids_edificios))
#         .group_by(ConsumoHistorico.anio, ConsumoHistorico.mes)
#         .order_by(ConsumoHistorico.anio, ConsumoHistorico.mes)
#     )
#     resultados = db.execute(stmt).all()
#     data = [dict(r._mapping) for r in resultados]
#     df = pd.DataFrame(data)
#     if df.empty: return []
#     if "consumo_kwh" in df.columns: df["consumo_kwh"] = pd.to_numeric(df["consumo_kwh"])
#     df["tendencia"] = df["consumo_kwh"].rolling(window=window, min_periods=1).mean()
#     df = df.where(pd.notnull(df), None)
#     return df.to_dict(orient="records")

# def ranking_interno_usuario(db: Session, ids_edificios: List[int], anio: int) -> Dict:
#     if not ids_edificios: return {"nombres": [], "valores": []}
#     stmt = (
#         select(
#             Edificio.nombre_edificio,
#             func.sum(ConsumoHistorico.consumo_kwh).label("total")
#         )
#         .join(Edificio.consumos)
#         .where(
#             ConsumoHistorico.edificio_id.in_(ids_edificios),
#             ConsumoHistorico.anio == anio
#         )
#         .group_by(Edificio.nombre_edificio)
#         .order_by(desc("total"))
#         .limit(10)
#     )
#     resultados = db.execute(stmt).all()
#     return {
#         "nombres": [r.nombre_edificio for r in resultados],
#         "valores": [float(r.total) for r in resultados]
#     }
