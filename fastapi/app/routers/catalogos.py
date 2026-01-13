# ============================================================
#  app/routers/catalogos.py
#  Endpoints para llenar selectores (Dropdowns)
# ============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from app.db.connection import get_session
from app.db.models import Sector, Dependencia, Edificio
from app.schemas.catalogos_schemas import SectorDTO, DependenciaDTO, EdificioDTO

router = APIRouter(
    prefix="/catalogos",
    tags=["Catálogos Públicos"]
)

# ------------------------------------------------------------
# 1. Obtener todos los Sectores
# ------------------------------------------------------------
@router.get("/sectores", response_model=List[SectorDTO])
def get_sectores(db: Session = Depends(get_session)):
    """Lista todos los sectores disponibles."""
    stmt = select(Sector.id_sector, Sector.nombre_sector).order_by(Sector.nombre_sector)
    results = db.execute(stmt).all()
    
    return [{"id": r.id_sector, "nombre": r.nombre_sector} for r in results]


# ------------------------------------------------------------
# 2. Obtener Dependencias por Sector
# ------------------------------------------------------------
@router.get("/dependencias/{sector_id}", response_model=List[DependenciaDTO])
def get_dependencias_por_sector(sector_id: int, db: Session = Depends(get_session)):
    """Lista dependencias filtradas por sector."""
    stmt = (
        select(Dependencia.id_dependencia, Dependencia.nombre_dependencia, Dependencia.sector_id)
        .where(Dependencia.sector_id == sector_id)
        .order_by(Dependencia.nombre_dependencia)
    )
    results = db.execute(stmt).all()

    return [
        {
            "id": r.id_dependencia, 
            "nombre": r.nombre_dependencia, 
            "sector_id": r.sector_id
        } 
        for r in results
    ]


# ------------------------------------------------------------
# 3. Obtener Edificios por Dependencia
# ------------------------------------------------------------
@router.get("/edificios/{dependencia_id}", response_model=List[EdificioDTO])
def get_edificios_por_dependencia(dependencia_id: int, db: Session = Depends(get_session)):
    """Lista edificios filtrados por dependencia."""
    stmt = (
        select(Edificio.id_edificio, Edificio.nombre_edificio, Edificio.dependencia_id)
        .where(Edificio.dependencia_id == dependencia_id)
        .order_by(Edificio.nombre_edificio)
    )
    results = db.execute(stmt).all()

    return [
        {
            "id": r.id_edificio, 
            "nombre": r.nombre_edificio, 
            "dependencia_id": r.dependencia_id
        } 
        for r in results
    ]