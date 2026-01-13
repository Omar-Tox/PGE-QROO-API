from sqlalchemy.orm import Session
from sqlalchemy import func, select
from app.db.models import ConsumoHistorico, Edificio, Dependencia, Sector

def obtener_consumo_historico(db: Session, anio: int):
    """
    Obtiene consumo total (kWh y costo) por edificio para un año.
    Usa la sintaxis moderna de SQLAlchemy 2.0.
    """
    stmt = (
        select(
            ConsumoHistorico.id_edificio,
            func.sum(ConsumoHistorico.consumo_kwh).label("total_kwh"),
            func.sum(ConsumoHistorico.costo_total).label("total_costo")
        )
        .where(ConsumoHistorico.anio == anio)
        .group_by(ConsumoHistorico.id_edificio)
    )
    return db.execute(stmt).all()


def obtener_consumo_por_sector(db: Session, anio: int, id_sector: int):
    """
    Obtiene el consumo total (kWh y costo) para un sector específico
    en un año determinado, usando la sintaxis 2.0.
    """
    stmt = (
        select(
            Sector.nombre_sector,
            func.sum(ConsumoHistorico.consumo_kwh).label("total_kwh"),
            func.sum(ConsumoHistorico.costo_total).label("total_costo")
        )
        # Hacemos JOIN usando las relaciones definidas en los modelos
        .join(Sector.dependencias)  # Relación Sector -> Dependencia
        .join(Dependencia.edificios) # Relación Dependencia -> Edificio
        .join(Edificio.consumos)     # Relación Edificio -> ConsumoHistorico
        .where(ConsumoHistorico.anio == anio)
        .where(Sector.id_sector == id_sector)
        .group_by(Sector.nombre_sector)
    )
    return db.execute(stmt).first()


def obtener_consumo_por_dependencia(db: Session, anio: int, id_dependencia: int):
    """
    Obtiene el consumo total (kWh y costo) para una dependencia específica
    en un año determinado, usando la sintaxis 2.0.
    """
    stmt = (
        select(
            Dependencia.nombre_dependencia,
            func.sum(ConsumoHistorico.consumo_kwh).label("total_kwh"),
            func.sum(ConsumoHistorico.costo_total).label("total_costo")
        )
        # Hacemos JOIN usando las relaciones
        .join(Dependencia.edificios) # Relación Dependencia -> Edificio
        .join(Edificio.consumos)     # Relación Edificio -> ConsumoHistorico
        .where(ConsumoHistorico.anio == anio)
        .where(Dependencia.id_dependencia == id_dependencia)
        .group_by(Dependencia.nombre_dependencia)
    )
    return db.execute(stmt).first()