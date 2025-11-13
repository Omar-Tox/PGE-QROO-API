from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ConsumoHistoricoBase(BaseModel):
    id_edificio: int
    anio: int
    mes: int
    consumo_kwh: float
    costo_total: float
    fuente_dato: Optional[str] = None

class ConsumoHistoricoCreate(ConsumoHistoricoBase):
    pass  # para inserciones futuras

class ConsumoHistorico(ConsumoHistoricoBase):
    id: int
    fecha_registro: datetime

    class Config:
        from_attributes = True  # compatibilidad con psycopg/sqlalchemy
