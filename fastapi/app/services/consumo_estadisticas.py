# app/services/consumo_estadisticas.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models import ConsumoHistorico


class ConsumoEstadisticasService:

    @staticmethod
    async def promedio_mensual_por_edificio(db: AsyncSession, id_edificio: int):
        """
        Calcula el promedio mensual de kWh y costo de un edificio.
        Retorna una lista de 12 meses (1–12) o solo los existentes.
        """

        query = (
            select(
                ConsumoHistorico.mes,
                func.avg(ConsumoHistorico.consumo_kwh).label("promedio_kwh"),
                func.avg(ConsumoHistorico.costo_total).label("promedio_costo")
            )
            .where(ConsumoHistorico.id_edificio == id_edificio)
            .group_by(ConsumoHistorico.mes)
            .order_by(ConsumoHistorico.mes)
        )

        result = await db.execute(query)
        rows = result.mappings().all()

        return [
            {
                "mes": r["mes"],
                "promedio_kwh": float(r["promedio_kwh"]),
                "promedio_costo": float(r["promedio_costo"])
            }
            for r in rows
        ]
