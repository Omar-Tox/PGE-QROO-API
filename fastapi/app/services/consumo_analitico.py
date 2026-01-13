# app/services/consumo_analitico.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models import ConsumoHistorico, Edificio, Dependencia, Sector


class ConsumoAnaliticoService:

    # ---------------------------------------------------
    # 🔹 1) TENDENCIA ANUAL (regresión lineal)
    # ---------------------------------------------------
    @staticmethod
    async def tendencia_anual(db: AsyncSession, id_edificio: int):
        query = (
            select(
                ConsumoHistorico.anio,
                func.sum(ConsumoHistorico.consumo_kwh).label("total_kwh")
            )
            .where(ConsumoHistorico.id_edificio == id_edificio)
            .group_by(ConsumoHistorico.anio)
            .order_by(ConsumoHistorico.anio)
        )

        rows = (await db.execute(query)).mappings().all()

        if len(rows) < 2:
            return {
                "tendencia": "no-suficientes-datos",
                "pendiente": 0,
                "intercepto": 0,
                "detalles": rows
            }

        # -------- Regresión lineal simple (x=años , y=consumo) --------
        x = [r["anio"] for r in rows]
        y = [float(r["total_kwh"]) for r in rows]

        n = len(rows)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum([x[i] * y[i] for i in range(n)])
        sum_x2 = sum([xi * xi for xi in x])

        pendiente = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercepto = (sum_y - pendiente * sum_x) / n

        tendencia = (
            "sube" if pendiente > 0 else
            "baja" if pendiente < 0 else
            "estable"
        )

        return {
            "tendencia": tendencia,
            "pendiente": pendiente,
            "intercepto": intercepto,
            "datos": rows
        }

    # ---------------------------------------------------
    # 🔹 2) DESGLOSE por Depedencia y Sector
    # ---------------------------------------------------
    @staticmethod
    async def desglose_dependencia_sector(db: AsyncSession):
        query = (
            select(
                Dependencia.nombre_dependencia,
                Sector.nombre_sector,
                func.sum(ConsumoHistorico.consumo_kwh).label("total_kwh"),
                func.sum(ConsumoHistorico.costo_total).label("total_costo")
            )
            .join(Edificio, Edificio.id_dependencia == Dependencia.id_dependencia)
            .join(Sector, Sector.id_sector == Dependencia.id_sector)
            .join(ConsumoHistorico, ConsumoHistorico.id_edificio == Edificio.id_edificio)
            .group_by(Dependencia.nombre_dependencia, Sector.nombre_sector)
            .order_by(Sector.nombre_sector, Dependencia.nombre_dependencia)
        )

        rows = (await db.execute(query)).mappings().all()

        return [
            {
                "dependencia": r["nombre_dependencia"],
                "sector": r["nombre_sector"],
                "total_kwh": float(r["total_kwh"]),
                "total_costo": float(r["total_costo"])
            }
            for r in rows
        ]

    # ---------------------------------------------------
    # 🔹 3) SERVICIO COMBINADO
    # ---------------------------------------------------
    @staticmethod
    async def analisis_general(db: AsyncSession, id_edificio: int):
        tendencia = await ConsumoAnaliticoService.tendencia_anual(db, id_edificio)
        desglose = await ConsumoAnaliticoService.desglose_dependencia_sector(db)

        return {
            "tendencia": tendencia,
            "desglose": desglose
        }
