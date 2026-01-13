# ============================================================
#  app/routers/analisis.py
#  Endpoints PRIVADOS Consolidados + Filtro Opcional
#  Incluye: KPIs, Gráficas y Estructura de Recursos
# ============================================================

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.db.connection import get_session
from app.services import analisis_service as service
from app.core.security import get_current_user
from app.db.models import User
from app.schemas.analisis_schemas import (
    DashboardKpisResponse, 
    DashboardEvolucionResponse, 
    DashboardTendenciaResponse, 
    DashboardRankingResponse,
    MisRecursosResponse 
)

router = APIRouter(
    prefix="/analisis",
    tags=["Dashboard Privado (Mi Dependencia)"]
)

# ------------------------------------------------------------
# 1. Dashboard KPIs (Resumen Ejecutivo)
# ------------------------------------------------------------
@router.get("/dashboard/kpis", summary="Resumen Financiero Anual", response_model=DashboardKpisResponse)
def dashboard_kpis(
    anio: int = Query(..., example=2024),
    dependencia_id: Optional[int] = Query(None, description="Opcional: Filtrar por ID de una dependencia"),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene el estado financiero real:
    - **Gasto Real:** Suma de recibos de luz de los edificios.
    - **Presupuesto:** Dinero asignado a la(s) dependencia(s).
    - **Balance:** Cuánto queda (o cuánto falta).
    """
    ids = service.obtener_edificios_usuario(db, current_user.id_usuario, dependencia_id)
    
    # Si no hay edificios, retornamos estructura vacía pero válida
    if not ids:
        if dependencia_id:
            raise HTTPException(status_code=403, detail="No tienes acceso a esta dependencia")
        return service.kpis_anuales(db, [], anio)

    return service.kpis_anuales(db, ids, anio)


# ------------------------------------------------------------
# 2. Dashboard Gráfica Temporal (Evolución)
# ------------------------------------------------------------
@router.get("/dashboard/evolucion", summary="Gráfica Mensual", response_model=DashboardEvolucionResponse)
def dashboard_evolucion(
    anio: int = Query(..., example=2024),
    dependencia_id: Optional[int] = Query(None),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    ids = service.obtener_edificios_usuario(db, current_user.id_usuario, dependencia_id)
    return service.evolucion_mensual_agregada(db, ids, anio)


# ------------------------------------------------------------
# 3. Dashboard Tendencia (Histórico)
# ------------------------------------------------------------
@router.get("/dashboard/tendencia", summary="Tendencia Histórica", response_model=DashboardTendenciaResponse)
def dashboard_tendencia(
    window: int = Query(3, ge=1, le=12),
    dependencia_id: Optional[int] = Query(None),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    ids = service.obtener_edificios_usuario(db, current_user.id_usuario, dependencia_id)
    return service.tendencia_agregada(db, ids, window)


# ------------------------------------------------------------
# 4. Dashboard Ranking (Mis Edificios)
# ------------------------------------------------------------
@router.get("/dashboard/ranking", summary="Top Consumo Interno", response_model=DashboardRankingResponse)
def dashboard_ranking(
    anio: int = Query(..., example=2024),
    dependencia_id: Optional[int] = Query(None),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    ids = service.obtener_edificios_usuario(db, current_user.id_usuario, dependencia_id)
    return service.ranking_interno_usuario(db, ids, anio)


# ------------------------------------------------------------
# 5. Estructura de Recursos (Para Filtros)
# ------------------------------------------------------------
@router.get("/dashboard/mis-recursos", summary="Obtener mis Dependencias y Edificios", response_model=MisRecursosResponse)
def obtener_mis_recursos(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    return service.obtener_estructura_recursos_usuario(db, current_user.id_usuario)
# # ------------------------------------------------------------
# # 1. Dashboard KPIs (Resumen Ejecutivo)
# # ------------------------------------------------------------
# @router.get("/dashboard/kpis", summary="Resumen Ejecutivo Anual")
# def dashboard_kpis(
#     anio: int = Query(..., example=2024),
#     dependencia_id: Optional[int] = Query(None, description="Opcional: Filtrar por ID de una dependencia específica permitida"),
#     db: Session = Depends(get_session),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Obtiene los indicadores clave (KPIs).
#     Si se envía 'dependencia_id', muestra solo los datos de esa dependencia (si tiene permiso).
#     Si no, muestra el agregado de TODAS sus dependencias.
#     """
#     ids = service.obtener_edificios_usuario(db, current_user.id_usuario, dependencia_id)
    
#     if not ids:
#         if dependencia_id:
#             raise HTTPException(status_code=403, detail="No tienes acceso a esta dependencia o no tiene edificios")
#         return {"mensaje": "No tienes edificios asignados", "kpis": {}}

#     return service.kpis_anuales(db, ids, anio)


# # ------------------------------------------------------------
# # 2. Dashboard Gráfica Temporal (Evolución)
# # ------------------------------------------------------------
# @router.get("/dashboard/evolucion", summary="Gráfica Mensual (kWh y $)")
# def dashboard_evolucion(
#     anio: int = Query(..., example=2024),
#     dependencia_id: Optional[int] = Query(None, description="Opcional: Filtrar por dependencia"),
#     db: Session = Depends(get_session),
#     current_user: User = Depends(get_current_user)
# ):
#     ids = service.obtener_edificios_usuario(db, current_user.id_usuario, dependencia_id)
#     return service.evolucion_mensual_agregada(db, ids, anio)


# # ------------------------------------------------------------
# # 3. Dashboard Tendencia (Histórico)
# # ------------------------------------------------------------
# @router.get("/dashboard/tendencia", summary="Tendencia Histórica (Rolling Mean)")
# def dashboard_tendencia(
#     window: int = Query(3, ge=1, le=12),
#     dependencia_id: Optional[int] = Query(None, description="Opcional: Filtrar por dependencia"),
#     db: Session = Depends(get_session),
#     current_user: User = Depends(get_current_user)
# ):
#     ids = service.obtener_edificios_usuario(db, current_user.id_usuario, dependencia_id)
#     return service.tendencia_agregada(db, ids, window)


# # ------------------------------------------------------------
# # 4. Dashboard Ranking (Mis Edificios)
# # ------------------------------------------------------------
# @router.get("/dashboard/ranking", summary="Top Consumo Interno")
# def dashboard_ranking(
#     anio: int = Query(..., example=2024),
#     dependencia_id: Optional[int] = Query(None, description="Opcional: Filtrar por dependencia"),
#     db: Session = Depends(get_session),
#     current_user: User = Depends(get_current_user)
# ):
#     ids = service.obtener_edificios_usuario(db, current_user.id_usuario, dependencia_id)
#     return service.ranking_interno_usuario(db, ids, anio)


# # ============================================================
# #  app/routers/analisis.py
# #  Endpoints PRIVADOS Consolidados
# # ============================================================

# from fastapi import APIRouter, Depends, Query, HTTPException
# from sqlalchemy.orm import Session

# from app.db.connection import get_session
# from app.services import analisis_service as service
# from app.core.security import get_current_user
# from app.db.models import User

# router = APIRouter(
#     prefix="/analisis",
#     tags=["Dashboard Privado (Mi Dependencia)"]
# )

# # ------------------------------------------------------------
# # 1. Dashboard KPIs (Resumen Ejecutivo)
# # ------------------------------------------------------------
# @router.get("/dashboard/kpis", summary="Resumen Ejecutivo Anual")
# def dashboard_kpis(
#     anio: int = Query(..., example=2024),
#     db: Session = Depends(get_session),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Obtiene los indicadores clave (KPIs) agregados de TODOS los edificios 
#     a los que el usuario tiene acceso (vía usuario_dependencia_roles).
#     """
#     # 1. Obtener IDs permitidos para este usuario
#     ids = service.obtener_edificios_usuario(db, current_user.id_usuario)
    
#     if not ids:
#         # Si el usuario existe pero no tiene dependencias asignadas
#         return {"mensaje": "No tienes edificios asignados", "kpis": {}}

#     # 2. Calcular KPIs agregados
#     return service.kpis_anuales(db, ids, anio)


# # ------------------------------------------------------------
# # 2. Dashboard Gráfica Temporal (Evolución)
# # ------------------------------------------------------------
# @router.get("/dashboard/evolucion", summary="Gráfica Mensual (kWh y $)")
# def dashboard_evolucion(
#     anio: int = Query(..., example=2024),
#     db: Session = Depends(get_session),
#     current_user: User = Depends(get_current_user)
# ):
#     ids = service.obtener_edificios_usuario(db, current_user.id_usuario)
#     return service.evolucion_mensual_agregada(db, ids, anio)


# # ------------------------------------------------------------
# # 3. Dashboard Tendencia (Histórico)
# # ------------------------------------------------------------
# @router.get("/dashboard/tendencia", summary="Tendencia Histórica (Rolling Mean)")
# def dashboard_tendencia(
#     window: int = Query(3, ge=1, le=12),
#     db: Session = Depends(get_session),
#     current_user: User = Depends(get_current_user)
# ):
#     ids = service.obtener_edificios_usuario(db, current_user.id_usuario)
#     return service.tendencia_agregada(db, ids, window)


# # ------------------------------------------------------------
# # 4. Dashboard Ranking (Mis Edificios)
# # ------------------------------------------------------------
# @router.get("/dashboard/ranking", summary="Top Consumo Interno")
# def dashboard_ranking(
#     anio: int = Query(..., example=2024),
#     db: Session = Depends(get_session),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Muestra cuáles de TUS edificios están consumiendo más energía.
#     """
#     ids = service.obtener_edificios_usuario(db, current_user.id_usuario)
#     return service.ranking_interno_usuario(db, ids, anio)