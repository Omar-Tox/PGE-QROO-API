# app/services/prediccion_service.py

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import ConsumoHistorico


class PrediccionService:

    # ==========================================================
    # 🔹 1) OBTENER SERIE MENSUAL ORDENADA
    # ==========================================================
    @staticmethod
    async def obtener_serie_mensual(db: AsyncSession, id_edificio: int):
        query = (
            select(
                ConsumoHistorico.anio,
                ConsumoHistorico.mes,
                ConsumoHistorico.consumo_kwh
            )
            .where(ConsumoHistorico.id_edificio == id_edificio)
            .order_by(ConsumoHistorico.anio, ConsumoHistorico.mes)
        )

        rows = (await db.execute(query)).mappings().all()

        # Convertimos a una lista de puntos
        serie = [
            {
                "anio": r["anio"],
                "mes": r["mes"],
                "consumo_kwh": float(r["consumo_kwh"])
            }
            for r in rows
        ]

        return serie

    # ==========================================================
    # 🔹 2) SUAVIZAMIENTO EXPONENCIAL SIMPLE (SES)
    # ==========================================================
    @staticmethod
    def ses_prediccion(valores, alpha=0.35):
        """
        valores: lista de números (consumo mensual)
        alpha: factor de suavizamiento (0.1 – 0.5 recomendado)
        """
        if not valores:
            return None

        # inicialización SES (primer valor)
        pron = valores[0]

        for v in valores:
            pron = alpha * v + (1 - alpha) * pron

        return pron  # este es el pronóstico del siguiente período

    # ==========================================================
    # 🔹 3) PREDICCIÓN FINAL
    # ==========================================================
    @staticmethod
    async def predecir_consumo(db: AsyncSession, id_edificio: int, meses_a_predecir=3):
        serie = await PrediccionService.obtener_serie_mensual(db, id_edificio)

        if len(serie) < 3:
            return {
                "status": "error",
                "detalle": "No hay suficientes datos para predecir"
            }

        valores = [p["consumo_kwh"] for p in serie]

        # Modelo base SES
        pred_base = PrediccionService.ses_prediccion(valores)

        # Último año/mes real
        ultimo = serie[-1]
        anio = ultimo["anio"]
        mes = ultimo["mes"]

        predicciones = []

        for i in range(meses_a_predecir):
            mes += 1
            if mes > 12:
                mes = 1
                anio += 1

            # Usamos el valor SES como base
            pred = pred_base

            # Ajuste por tendencia simple: diferencia promedio
            if len(valores) >= 6:
                difs = [valores[i] - valores[i - 1] for i in range(1, len(valores))]
                ajuste = sum(difs) / len(difs)
                pred += ajuste

            predicciones.append({
                "anio": anio,
                "mes": mes,
                "consumo_kwh_predicho": round(pred, 2)
            })

            # Alimentar el modelo incrementalmente
            valores.append(pred)

            pred_base = PrediccionService.ses_prediccion(valores)

        return {
            "status": "ok",
            "historico_meses": len(serie),
            "predicciones": predicciones
        }
        # ==========================================================
    
    # 🔹 B5 — TARIFA PROMEDIO HISTÓRICA
    # ==========================================================
    @staticmethod
    async def obtener_tarifa_promedio(db: AsyncSession, id_edificio: int):
        query = (
            select(
                func.sum(ConsumoHistorico.costo_total).label("total_costo"),
                func.sum(ConsumoHistorico.consumo_kwh).label("total_kwh")
            )
            .where(ConsumoHistorico.id_edificio == id_edificio)
        )

        row = (await db.execute(query)).mappings().first()

        if not row or row["total_kwh"] is None:
            return None

        tarifa = float(row["total_costo"]) / float(row["total_kwh"])
        return tarifa

    # ==========================================================
    # 🔹 B5 — PREDICCIÓN DE COSTOS
    # ==========================================================
    @staticmethod
    async def predecir_costos(
        db: AsyncSession,
        id_edificio: int,
        meses_a_predecir=3,
        tarifa_personalizada: float | None = None
    ):
        # 1) obtener predicción de consumo (usamos B4)
        resultado_consumo = await PrediccionService.predecir_consumo(
            db,
            id_edificio,
            meses_a_predecir
        )

        if resultado_consumo["status"] != "ok":
            return resultado_consumo

        predicciones_consumo = resultado_consumo["predicciones"]

        # 2) tarifa promedio histórica
        tarifa_promedio = await PrediccionService.obtener_tarifa_promedio(db, id_edificio)

        if tarifa_promedio is None:
            return {
                "status": "error",
                "detalle": "No hay datos suficientes para calcular tarifa promedio."
            }

        # 3) si hay tarifa personalizada, sobrescribe
        tarifa_final = tarifa_personalizada if tarifa_personalizada else tarifa_promedio

        # 4) calcular costos
        predicciones_costos = []

        for p in predicciones_consumo:
            costo = p["consumo_kwh_predicho"] * tarifa_final

            predicciones_costos.append({
                "anio": p["anio"],
                "mes": p["mes"],
                "consumo_kwh_predicho": p["consumo_kwh_predicho"],
                "costo_predicho": round(costo, 2),
                "tarifa_utilizada": round(tarifa_final, 4)
            })

        return {
            "status": "ok",
            "tarifa_promedio_historica": round(tarifa_promedio, 4),
            "tarifa_usada": round(tarifa_final, 4),
            "predicciones": predicciones_costos
        }
        # ==========================================================
    # 🔮 B6 — WHAT-IF SCENARIOS
    # ==========================================================
    @staticmethod
    async def what_if(
        db: AsyncSession,
        id_edificio: int,
        meses_a_predecir: int = 3,
        variacion_consumo: float | None = None,   # -0.10 = baja 10%, 0.15 = sube 15%
        variacion_tarifa: float | None = None,    # -0.05 = baja 5%, 0.20 = sube 20%
        tarifas_personalizadas: dict | None = None
    ):
        """
        Escenarios tipo what-if.
        """

        # ==========================================
        # 1) Primero obtenemos las predicciones base
        # ==========================================
        base = await PrediccionService.predecir_costos(
            db,
            id_edificio,
            meses_a_predecir
        )

        if base["status"] != "ok":
            return base

        pred_base = base["predicciones"]
        tarifa_base = base["tarifa_usada"]

        resultados = []

        # ==========================================
        # 2) Procesar cada mes predicho
        # ==========================================
        for pred in pred_base:

            consumo = pred["consumo_kwh_predicho"]
            tarifa = tarifa_base

            # ---- A) Variación EXCEL tipo (%) en consumo ----
            if variacion_consumo is not None:
                consumo = consumo * (1 + variacion_consumo)

            # ---- B) Variación global de tarifa ----
            if variacion_tarifa is not None:
                tarifa = tarifa * (1 + variacion_tarifa)

            # ---- C) Tarifa personalizada por mes ----
            if tarifas_personalizadas:
                key = f"{pred['anio']}-{pred['mes']}"
                if key in tarifas_personalizadas:
                    tarifa = tarifas_personalizadas[key]

            costo = consumo * tarifa

            resultados.append({
                "anio": pred["anio"],
                "mes": pred["mes"],

                "consumo_simulado_kwh": round(consumo, 2),
                "tarifa_simulada": round(tarifa, 4),
                "costo_simulado": round(costo, 2),

                "base_consumo_kwh": pred["consumo_kwh_predicho"],
                "base_tarifa": tarifa_base,
                "base_costo": pred["costo_predicho"]
            })

        return {
            "status": "ok",
            "escenario": {
                "variacion_consumo": variacion_consumo,
                "variacion_tarifa": variacion_tarifa,
                "tarifas_personalizadas": tarifas_personalizadas
            },
            "resultados": resultados
        }
        
    
 


