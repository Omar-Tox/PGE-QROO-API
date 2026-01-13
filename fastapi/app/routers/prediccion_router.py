# ============================================================
#  app/routers/prediccion_router.py
#  Router para Predicciones (Multi-Horizonte + Rangos)
# ============================================================

from fastapi import APIRouter, Depends, Query, HTTPException, Request, Response
from sqlalchemy.orm import Session
from typing import Optional

from app.db.connection import get_session
from app.core.security import get_current_user
from app.db.models import User
from app.services import analisis_service, prediccion_service, ia_service
from app.core.limiter import limiter 

router = APIRouter(
    prefix="/prediccion",
    tags=["Predicciones (Inteligencia)"]
)

def _validar_y_obtener_ids(db: Session, user_id: int, dependencia_id: Optional[int]) -> tuple[list[int], dict]:
    mis_dependencias = analisis_service.obtener_mis_dependencias_ids(db, user_id)
    if not mis_dependencias:
        raise HTTPException(status_code=404, detail="El usuario no tiene dependencias asignadas.")

    target_dep_id = None
    if dependencia_id:
        if dependencia_id not in mis_dependencias:
            raise HTTPException(status_code=403, detail="No tienes acceso a la dependencia solicitada.")
        target_dep_id = dependencia_id
    else:
        target_dep_id = mis_dependencias[0]

    nombre_dep = analisis_service.obtener_nombre_dependencia(db, target_dep_id)
    ids_edificios = analisis_service.obtener_edificios_usuario(db, user_id, target_dep_id)
    
    if not ids_edificios:
        raise HTTPException(status_code=404, detail=f"La dependencia '{nombre_dep}' no tiene edificios con datos.")
        
    contexto = {
        "dependencia_id": target_dep_id,
        "dependencia_nombre": nombre_dep,
        "edificios_incluidos": len(ids_edificios)
    }
    return ids_edificios, contexto


# ------------------------------------------------------------
#  ENDPOINT 1: Proyección Matemática (Con Horizonte y Filtro)
# ------------------------------------------------------------
@router.get("/proyeccion-matematica", summary="🔮 Predicción Numérica (Fase A)")
def obtener_proyeccion_matematica(
    meses: int = Query(6, description="Horizonte de proyección (6, 12, 24 meses)", enum=[6, 12, 24]),
    ver_todo_historial: bool = Query(True, description="Si es False, la gráfica solo devuelve datos del año actual (o recientes)."),
    dependencia_id: Optional[int] = Query(None, description="ID de la dependencia."),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Calcula la proyección matemática.
    
    - **Rango de Precios:** Incluye un estimado mínimo y máximo basado en la variabilidad histórica.
    - **Filtro:** Usa `ver_todo_historial=False` si solo quieres visualizar el año en curso + predicción.
    """
    ids_edificios, contexto = _validar_y_obtener_ids(db, current_user.id_usuario, dependencia_id)

    # Pasamos el nuevo parámetro 'solo_anio_actual' (es el inverso de ver_todo_historial)
    resultado = prediccion_service.calcular_proyeccion_matematica(
        db, 
        ids_edificios, 
        meses_a_proyectar=meses, 
        solo_anio_actual=not ver_todo_historial
    )
    resultado["contexto_analisis"] = contexto

    return resultado


# ------------------------------------------------------------
#  ENDPOINT 2: Análisis con IA (Con Horizonte y Filtro)
# ------------------------------------------------------------
@router.get("/ia-analisis-estrategico", summary="🧠 Consultoría IA (Fase B)")
@limiter.limit("10/hour")
def obtener_analisis_ia(
    request: Request, 
    response: Response,
    meses: int = Query(6, description="Horizonte de análisis.", enum=[6, 12, 24]),
    ver_todo_historial: bool = Query(True, description="Afecta los datos que se muestran en la gráfica adjunta."),
    dependencia_id: Optional[int] = Query(None, description="ID de la dependencia."),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    ids_edificios, contexto = _validar_y_obtener_ids(db, current_user.id_usuario, dependencia_id)
    
    # Calculamos la proyección
    datos_matematicos = prediccion_service.calcular_proyeccion_matematica(
        db, 
        ids_edificios, 
        meses_a_proyectar=meses,
        solo_anio_actual=not ver_todo_historial
    )
    datos_matematicos["contexto_analisis"] = contexto
    
    # La IA recibe el contexto de tiempo
    reporte_inteligente = ia_service.generar_analisis_ejecutivo(datos_matematicos)
    
    reporte_inteligente["meta_uso"] = {
        "limite_politica": "10 peticiones por hora",
        "horizonte_seleccionado": f"{meses} meses"
    }
    
    # Inyectamos también los datos numéricos mejorados (con rango) para que el frontend los use
    reporte_inteligente["datos_proyeccion"] = datos_matematicos
    
    return reporte_inteligente