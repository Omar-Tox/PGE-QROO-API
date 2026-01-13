from pydantic import BaseModel
from typing import Optional

class PresupuestoBase(BaseModel):
    id_dependencia: int
    anio: int
    trimestre: int
    monto_asignado: float

class PresupuestoCreate(PresupuestoBase):
    pass  # útil para inserciones nuevas

class Presupuesto(PresupuestoBase):
    id_presupuesto: int

    class Config:
        from_attributes = True
