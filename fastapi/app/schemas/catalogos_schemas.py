# app/schemas/catalogos_schemas.py

from pydantic import BaseModel

class SectorDTO(BaseModel):
    id: int
    nombre: str

class DependenciaDTO(BaseModel):
    id: int
    nombre: str
    sector_id: int

class EdificioDTO(BaseModel):
    id: int
    nombre: str
    dependencia_id: int