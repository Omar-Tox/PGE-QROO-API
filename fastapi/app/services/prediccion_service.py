# ============================================================
#  app/services/prediccion_service.py
#  FASE A MEJORADA: Regresión Lineal + Estacionalidad Reciente + Factor de Caos
# ============================================================

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List, Dict, Any
from datetime import datetime

from app.db.models import ConsumoHistorico

def _obtener_datos_historicos_agregados(db: Session, ids_edificios: List[int]) -> pd.DataFrame:
    """
    Obtiene y suma el consumo de todos los edificios solicitados.
    """
    if not ids_edificios:
        return pd.DataFrame()

    stmt = (
        select(
            ConsumoHistorico.anio,
            ConsumoHistorico.mes,
            func.sum(ConsumoHistorico.consumo_kwh).label("total_kwh"),
            func.sum(ConsumoHistorico.costo_total).label("total_costo")
        )
        .where(ConsumoHistorico.edificio_id.in_(ids_edificios))
        .group_by(ConsumoHistorico.anio, ConsumoHistorico.mes)
        .order_by(ConsumoHistorico.anio, ConsumoHistorico.mes)
    )
    
    resultados = db.execute(stmt).all()
    
    data = [dict(r._mapping) for r in resultados]
    df = pd.DataFrame(data)
    
    if not df.empty:
        df["total_kwh"] = df["total_kwh"].astype(float)
        df["total_costo"] = df["total_costo"].astype(float)
        df["indice_tiempo"] = range(1, len(df) + 1)
        
    return df

def _calcular_indices_estacionales_ponderados(df: pd.DataFrame, modelo_tendencia, col_valor="total_kwh") -> Dict[int, float]:
    """
    Calcula la estacionalidad basándose estrictamente en los datos proporcionados.
    """
    X = df[["indice_tiempo"]].values
    tendencia_pura = modelo_tendencia.predict(X)
    
    df = df.copy()
    # Evitamos división por cero
    df["ratio_estacional"] = df[col_valor] / (tendencia_pura + 0.0001)
    
    # Agrupamos por mes. Si hay pocos datos (ej. solo 1 enero), ese será el índice.
    # Si hay varios años, saca el promedio.
    indices_mensuales = df.groupby("mes")["ratio_estacional"].mean().to_dict()
    
    return indices_mensuales

def calcular_proyeccion_matematica(
    db: Session, 
    ids_edificios: List[int], 
    meses_a_proyectar: int = 6,
    solo_anio_actual: bool = False 
) -> Dict[str, Any]:
    """
    Predicción Adaptativa:
    - Si solo_anio_actual=True: Entrena SOLO con la historia reciente (más volátil y realista a corto plazo).
    - Si solo_anio_actual=False: Entrena con todo el historial (más estable y suavizado).
    """
    df_total = _obtener_datos_historicos_agregados(db, ids_edificios)

    if len(df_total) < 3:
        return {
            "status": "error",
            "mensaje": "Insuficientes datos históricos para predecir."
        }

    # --- 1. SELECCIÓN DE DATOS DE ENTRENAMIENTO (ADAPTABILIDAD) ---
    # Aquí decidimos qué "memoria" usar para el modelo
    if solo_anio_actual:
        # Si el usuario quiere ver "lo actual", usamos máximo los últimos 24 meses para entrenar.
        # Esto captura la tendencia "de moda" y la volatilidad reciente.
        window_size = 24
        if len(df_total) > window_size:
            df_entrenamiento = df_total.tail(window_size).copy()
        else:
            df_entrenamiento = df_total.copy()
    else:
        # Si quiere ver todo, usamos toda la historia (tendencia a largo plazo)
        df_entrenamiento = df_total.copy()

    # --- 2. ENTRENAMIENTO (TENDENCIA) ---
    X_train = df_entrenamiento[["indice_tiempo"]].values 
    y_kwh_train = df_entrenamiento["total_kwh"].values
    y_costo_train = df_entrenamiento["total_costo"].values

    modelo_kwh = LinearRegression()
    modelo_kwh.fit(X_train, y_kwh_train)
    
    modelo_costo = LinearRegression()
    modelo_costo.fit(X_train, y_costo_train)

    # --- 3. ESTACIONALIDAD Y VOLATILIDAD ---
    indices_kwh = _calcular_indices_estacionales_ponderados(df_entrenamiento, modelo_kwh, "total_kwh")
    indices_costo = _calcular_indices_estacionales_ponderados(df_entrenamiento, modelo_costo, "total_costo")

    # Calcular desviación estándar (Ruido) sobre los datos de entrenamiento
    pred_ajustada_kwh = modelo_kwh.predict(X_train) * [indices_kwh.get(m, 1.0) for m in df_entrenamiento["mes"]]
    residuos_kwh = y_kwh_train - pred_ajustada_kwh
    desviacion_kwh = np.std(residuos_kwh)

    pred_ajustada_costo = modelo_costo.predict(X_train) * [indices_costo.get(m, 1.0) for m in df_entrenamiento["mes"]]
    residuos_costo = y_costo_train - pred_ajustada_costo
    desviacion_costo = np.std(residuos_costo)

    # Métricas
    score_r2 = modelo_kwh.score(X_train, y_kwh_train)
    pendiente = modelo_kwh.coef_[0]
    
    estado_tendencia = "Estable"
    if pendiente > 50: estado_tendencia = "Creciente 📈"
    elif pendiente < -50: estado_tendencia = "Decreciente 📉"

    # --- 4. GENERACIÓN DE FUTURO ---
    # Usamos el último índice REAL del dataset total para continuar la línea de tiempo correctamente
    ultimo_indice = df_total["indice_tiempo"].iloc[-1]
    ultimo_anio = int(df_total["anio"].iloc[-1])
    ultimo_mes = int(df_total["mes"].iloc[-1])
    
    proyecciones = []
    
    # Preparamos datos para la gráfica (Respuesta Visual)
    # Si pidió solo año actual, recortamos lo que enviamos al frontend
    df_visual = df_total.copy()
    if solo_anio_actual:
        anio_hoy = datetime.now().year
        # Intentamos mostrar desde enero del año actual, si no hay, mostramos los ultimos 12 meses
        mask_anio = df_visual["anio"] == anio_hoy
        if not df_visual[mask_anio].empty:
            df_visual = df_visual[mask_anio]
        else:
            df_visual = df_visual.tail(12)
            
    datos_grafica = df_visual[["anio", "mes", "total_kwh", "total_costo"]].to_dict(orient="records")
    for d in datos_grafica:
        d["tipo"] = "real"

    # Bucle de Proyección
    anio_loop = ultimo_anio
    mes_loop = ultimo_mes

    acumulado_kwh = 0
    acumulado_costo = 0
    
    # Semilla fija para consistencia visual entre recargas, 
    # pero basada en el ID del edificio para que varíe entre edificios si se desea (opcional),
    # aquí usamos fija para estabilidad.
    np.random.seed(42)

    for i in range(1, meses_a_proyectar + 1):
        mes_loop += 1
        if mes_loop > 12:
            mes_loop = 1
            anio_loop += 1
        
        # A. Base Lineal (Usando el modelo entrenado recientemente)
        indice_futuro = np.array([[ultimo_indice + i]])
        base_kwh = modelo_kwh.predict(indice_futuro)[0]
        base_costo = modelo_costo.predict(indice_futuro)[0]
        
        # B. Factor Estacional
        # Si no tenemos datos para ese mes en el set de entrenamiento (ej. set muy corto), usamos 1.0
        factor_kwh = indices_kwh.get(mes_loop, 1.0)
        factor_costo = indices_costo.get(mes_loop, 1.0)
        
        # C. Factor de Caos (Realismo)
        # Usamos la desviación estándar calculada. 
        # Si el historial reciente es caótico, la predicción será caótica.
        ruido_kwh = np.random.normal(0, desviacion_kwh) 
        ruido_costo = np.random.normal(0, desviacion_costo)

        final_kwh = max(0, (base_kwh * factor_kwh) + ruido_kwh)
        final_costo = max(0, (base_costo * factor_costo) + ruido_costo)
        
        item = {
            "anio": anio_loop,
            "mes": mes_loop,
            "total_kwh": round(final_kwh, 2),
            "total_costo": round(final_costo, 2),
            "tipo": "prediccion",
            "rango_costo_min": max(0, round(final_costo - desviacion_costo, 2)),
            "rango_costo_max": round(final_costo + desviacion_costo, 2)
        }
        
        proyecciones.append(item)
        datos_grafica.append(item)
        
        acumulado_kwh += final_kwh
        acumulado_costo += final_costo

    costo_proyectado_total = round(acumulado_costo, 2)
    
    return {
        "status": "success",
        "metodo": f"Regresión Adaptativa ({'Datos Recientes' if solo_anio_actual else 'Historial Completo'})",
        "datos_analizados": len(df_entrenamiento), # Mostramos cuántos datos REALMENTE usó el modelo
        "confiabilidad_matematica": round(score_r2, 4),
        "resumen_proyeccion": {
            "horizonte_meses": meses_a_proyectar,
            "tendencia_detectada": estado_tendencia,
            "factor_crecimiento_mensual": round(pendiente, 2),
            "suma_total_kwh_proyectada": round(acumulado_kwh, 2),
            "suma_total_costo_proyectada": costo_proyectado_total,
            "rango_precios_estimado": {
                "minimo": max(0, round(costo_proyectado_total - (desviacion_costo * meses_a_proyectar), 2)),
                "maximo": round(costo_proyectado_total + (desviacion_costo * meses_a_proyectar), 2),
                "margen_error_promedio_mensual": round(desviacion_costo, 2)
            }
        },
        "detalle_proyeccion": proyecciones,
        "datos_para_grafica": datos_grafica,
        "filtro_historial_aplicado": "Solo año actual/reciente" if solo_anio_actual else "Historial completo"
    }