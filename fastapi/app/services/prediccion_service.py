# ============================================================
#  app/services/prediccion_service.py
#  FASE A: Motor Matemático (Regresión Lineal Multi-Horizonte)
#  MEJORADO: Rango de Precios (Margen de Error) + Filtro de Historial
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

def calcular_proyeccion_matematica(
    db: Session, 
    ids_edificios: List[int], 
    meses_a_proyectar: int = 6,
    solo_anio_actual: bool = False # 📌 NUEVO PARÁMETRO
) -> Dict[str, Any]:
    """
    Realiza una Regresión Lineal para predecir N meses a futuro.
    Incluye cálculo de margen de error (Rango de Precios).
    """
    df = _obtener_datos_historicos_agregados(db, ids_edificios)

    if len(df) < 3:
        return {
            "status": "error",
            "mensaje": "Insuficientes datos históricos para predecir (se requieren mínimo 3 meses)."
        }

    # --- ENTRENAMIENTO DEL MODELO ---
    X = df[["indice_tiempo"]].values 
    y_kwh = df["total_kwh"].values
    y_costo = df["total_costo"].values

    modelo_kwh = LinearRegression()
    modelo_kwh.fit(X, y_kwh)
    
    modelo_costo = LinearRegression()
    modelo_costo.fit(X, y_costo)

    # --- CÁLCULO DE MARGEN DE ERROR (NUEVO) ---
    # Calculamos la desviación estándar de los residuos (Realidad - Predicción del modelo)
    # Esto nos dice qué tanto suele equivocarse el modelo en pesos ($)
    predicciones_historicas_costo = modelo_costo.predict(X)
    residuos_costo = y_costo - predicciones_historicas_costo
    desviacion_estandar_costo = np.std(residuos_costo)
    
    # Usamos un multiplicador (ej. 1.96 para 95% confianza, o 1.0 para rango estándar)
    margen_error_costo = desviacion_estandar_costo

    # Calidad y Tendencia
    score_r2 = modelo_kwh.score(X, y_kwh)
    pendiente = modelo_kwh.coef_[0]
    estado_tendencia = "Estable"
    if pendiente > 50: estado_tendencia = "Creciente 📈"
    elif pendiente < -50: estado_tendencia = "Decreciente 📉"

    # --- GENERACIÓN DE FUTURO ---
    ultimo_indice = df["indice_tiempo"].iloc[-1]
    ultimo_anio = int(df["anio"].iloc[-1])
    ultimo_mes = int(df["mes"].iloc[-1])
    
    proyecciones = []
    
    # --- FILTRADO DE HISTORIAL PARA RESPUESTA ---
    # Si el usuario solo quiere ver el año actual, filtramos el DataFrame ANTES de convertirlo a dict
    df_respuesta = df.copy()
    if solo_anio_actual:
        anio_actual = datetime.now().year
        # Si no hay datos de este año (ej. estamos en enero), mostramos al menos el año anterior
        if not df_respuesta[df_respuesta["anio"] == anio_actual].empty:
            df_respuesta = df_respuesta[df_respuesta["anio"] == anio_actual]
        else:
            # Fallback: Mostrar últimos 12 meses si el año actual está vacío
            df_respuesta = df_respuesta.tail(12)

    datos_grafica = df_respuesta[["anio", "mes", "total_kwh", "total_costo"]].to_dict(orient="records")
    
    for d in datos_grafica:
        d["tipo"] = "real"

    # Bucle de Proyección
    anio_actual_loop = ultimo_anio
    mes_actual_loop = ultimo_mes

    acumulado_kwh = 0
    acumulado_costo = 0

    for i in range(1, meses_a_proyectar + 1):
        mes_actual_loop += 1
        if mes_actual_loop > 12:
            mes_actual_loop = 1
            anio_actual_loop += 1
        
        indice_futuro = np.array([[ultimo_indice + i]])
        pred_kwh = max(0, modelo_kwh.predict(indice_futuro)[0])
        pred_costo = max(0, modelo_costo.predict(indice_futuro)[0])
        
        item = {
            "anio": anio_actual_loop,
            "mes": mes_actual_loop,
            "total_kwh": round(pred_kwh, 2),
            "total_costo": round(pred_costo, 2),
            "tipo": "prediccion",
            # Agregamos el rango al objeto de gráfica para pintar "bandas" si el frontend lo soporta
            "rango_costo_min": max(0, round(pred_costo - margen_error_costo, 2)),
            "rango_costo_max": round(pred_costo + margen_error_costo, 2)
        }
        
        proyecciones.append(item)
        datos_grafica.append(item)
        
        acumulado_kwh += pred_kwh
        acumulado_costo += pred_costo

    # Valores totales proyectados con rango
    costo_proyectado_total = round(acumulado_costo, 2)
    rango_min_total = max(0, round(costo_proyectado_total - (margen_error_costo * meses_a_proyectar), 2)) # Margen acumulado simple
    rango_max_total = round(costo_proyectado_total + (margen_error_costo * meses_a_proyectar), 2)

    return {
        "status": "success",
        "metodo": f"Regresión Lineal (Proyección {meses_a_proyectar} meses)",
        "datos_analizados": len(df), # Total real usado para el cálculo
        "confiabilidad_matematica": round(score_r2, 4),
        "resumen_proyeccion": {
            "horizonte_meses": meses_a_proyectar,
            "tendencia_detectada": estado_tendencia,
            "factor_crecimiento_mensual": round(pendiente, 2),
            "suma_total_kwh_proyectada": round(acumulado_kwh, 2),
            "suma_total_costo_proyectada": costo_proyectado_total,
            
            # 📌 NUEVO: Rango de Precios Aproximado
            "rango_precios_estimado": {
                "minimo": rango_min_total,
                "maximo": rango_max_total,
                "margen_error_promedio_mensual": round(margen_error_costo, 2)
            }
        },
        "detalle_proyeccion": proyecciones,
        "datos_para_grafica": datos_grafica,
        "filtro_historial_aplicado": "Solo año actual/reciente" if solo_anio_actual else "Historial completo"
    }