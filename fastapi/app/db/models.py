# app/db/models.py

from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy import (
    String, Integer, ForeignKey, Numeric, TIMESTAMP, Text
)

class Base(DeclarativeBase):
    """Base declarativa para todos los modelos ORM."""
    pass


# ============================
# 📌 Tabla: sector
# ============================
class Sector(Base):
    __tablename__ = "sector"

    id_sector: Mapped[int] = mapped_column(primary_key=True)
    nombre_sector: Mapped[str] = mapped_column(String(100), unique=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)

    dependencias = relationship("Dependencia", back_populates="sector")


# ============================
# 📌 Tabla: dependencias
# ============================
class Dependencia(Base):
    __tablename__ = "dependencias"

    id_dependencia: Mapped[int] = mapped_column(primary_key=True)
    nombre_dependencia: Mapped[str] = mapped_column(String(255), unique=True)
    # FK correcta: sector_id
    sector_id: Mapped[int | None] = mapped_column(ForeignKey("sector.id_sector"))
    fecha_alta: Mapped[str] = mapped_column(TIMESTAMP)

    sector = relationship("Sector", back_populates="dependencias")
    edificios = relationship("Edificio", back_populates="dependencia")
    presupuestos = relationship("Presupuesto", back_populates="dependencia")


# ============================
# 📌 Tabla: edificio
# ============================
class Edificio(Base):
    __tablename__ = "edificio"

    id_edificio: Mapped[int] = mapped_column(primary_key=True)
    # FK correcta: dependencia_id
    dependencia_id: Mapped[int] = mapped_column(ForeignKey("dependencias.id_dependencia"))
    nombre_edificio: Mapped[str] = mapped_column(String(255))

    direccion: Mapped[str | None] = mapped_column(String(500))
    latitud: Mapped[float | None] = mapped_column(Numeric(9, 6))
    longitud: Mapped[float | None] = mapped_column(Numeric(9, 6))
    caracteristicas: Mapped[str | None] = mapped_column(Text)

    dependencia = relationship("Dependencia", back_populates="edificios")
    consumos = relationship("ConsumoHistorico", back_populates="edificio")


# ============================
# 📌 Tabla: consumo_historico
# ============================
class ConsumoHistorico(Base):
    __tablename__ = "consumo_historico"

    id: Mapped[int] = mapped_column(primary_key=True)
    # FK correcta: edificio_id
    edificio_id: Mapped[int] = mapped_column(ForeignKey("edificio.id_edificio"))

    # 📌 CORRECCIÓN CRÍTICA: Mapeamos el atributo 'anio' a la columna "año" de la DB
    anio: Mapped[int] = mapped_column("año", Integer)
    
    mes: Mapped[int] = mapped_column(Integer)

    consumo_kwh: Mapped[float] = mapped_column(Numeric(18, 2))
    costo_total: Mapped[float] = mapped_column(Numeric(18, 2))

    fuente_dato: Mapped[str | None] = mapped_column(String(100))
    fecha_registro: Mapped[str] = mapped_column(TIMESTAMP)

    edificio = relationship("Edificio", back_populates="consumos")


# ============================
# 📌 Tabla: presupuestos
# ============================
class Presupuesto(Base):
    __tablename__ = "presupuestos"

    id_presupuesto: Mapped[int] = mapped_column(primary_key=True)
    # FK correcta: dependencia_id
    dependencia_id: Mapped[int] = mapped_column(ForeignKey("dependencias.id_dependencia"))

    # 📌 CORRECCIÓN CRÍTICA: Mapeamos 'anio' a "año" aquí también
    anio: Mapped[int] = mapped_column("año", Integer)
    
    trimestre: Mapped[int] = mapped_column(Integer)
    monto_asignado: Mapped[float] = mapped_column(Numeric(18, 2))

    dependencia = relationship("Dependencia", back_populates="presupuestos")