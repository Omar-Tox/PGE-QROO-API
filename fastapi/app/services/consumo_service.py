# app/services/consumo_service.py

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.models import (
    ConsumoHistorico, Edificio, Dependencia
)


def consumo_total_por_anio(db: Session, anio: int, id_sector: int | None = None, id_dependencia: int | None = None):
    """
    Obtiene el consumo total (kWh y costo) de un año,
    con filtros opcionales por sector o dependencia.
    """

    # ==============================
    # 1. Construcción de la consulta base
    # ==============================
    query = (
        select(
            func.sum(ConsumoHistorico.consumo_kwh).label("total_kwh"),
            func.sum(ConsumoHistorico.costo_total).label("total_costo"),
            func.count(func.distinct(ConsumoHistorico.id_edificio)).label("num_edificios")
        )
        .join(Edificio, ConsumoHistorico.id_edificio == Edificio.id_edificio)
        .join(Dependencia, Edificio.id_dependencia == Dependencia.id_dependencia)
        .where(ConsumoHistorico.anio == anio)
    )

    # ==================================
    # 2. Filtros adicionales opcionales
    # ==================================
    if id_dependencia:
        query = query.where(Dependencia.id_dependencia == id_dependencia)

    if id_sector:
        query = query.where(Dependencia.id_sector == id_sector)

    # ==============================
    # 3. Ejecutar consulta
    # ==============================
    result = db.execute(query).mappings().first()

    # ==================================
    # 4. Datos mensuales desglosados
    # ==================================
    query_mensual = (
        select(
            ConsumoHistorico.mes,
            func.sum(ConsumoHistorico.consumo_kwh).label("kwh"),
            func.sum(ConsumoHistorico.costo_total).label("costo")
        )
        .join(Edificio, ConsumoHistorico.id_edificio == Edificio.id_edificio)
        .join(Dependencia, Edificio.id_dependencia == Dependencia.id_dependencia)
        .where(ConsumoHistorico.anio == anio)
        .group_by(ConsumoHistorico.mes)
        .order_by(ConsumoHistorico.mes)
    )

    if id_dependencia:
        query_mensual = query_mensual.where(Dependencia.id_dependencia == id_dependencia)

    if id_sector:
        query_mensual = query_mensual.where(Dependencia.id_sector == id_sector)

    result_mensual = db.execute(query_mensual).mappings().all()

    # ==============================
    # 5. Respuesta final formateada
    # ==============================
    return {
        "anio": anio,
        "filtros": {
            "id_sector": id_sector,
            "id_dependencia": id_dependencia
        },
        "totales": {
            "kwh": float(result["total_kwh"] or 0),
            "costo": float(result["total_costo"] or 0),
            "num_edificios": int(result["num_edificios"] or 0)
        },
        "mensual": [
            {
                "mes": r["mes"],
                "kwh": float(r["kwh"]),
                "costo": float(r["costo"])
            }
            for r in result_mensual
        ]
    }
