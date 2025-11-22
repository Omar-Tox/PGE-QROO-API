from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import psycopg # Driver directo para el test de DB (como lo tenías)

from app.core.config import settings

from app.core.limiter import limiter 
from app.routers import analisis, prediccion_router, catalogos, analisis_publico

app = FastAPI(
    title="PGE QROO API",
    description="""
API para análisis energético, histórico y predicción basada en consumo eléctrico.

Incluye:
- Análisis energético (consumo total, rankings, comparativas)
- Predicción de consumo (SES + tendencia)
- Simulaciones What-if
""",
    version="1.0.1"
)

# Registrar limiter en la app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ========================================================
# 🌐 CORS CONFIG (Dinámico desde settings)
# ========================================================
# Intentamos obtener la lista desde settings, si no existe, permitimos todo (dev mode)
origins = getattr(settings, "BACKEND_CORS_ORIGINS", ["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================================
# 📌 Registrar Routers (Versionado por API)
# ========================================================
app.include_router(analisis.router)
app.include_router(prediccion_router.router)
app.include_router(catalogos.router) 
app.include_router(analisis_publico.router)


# ========================================================
# 🏠 Endpoints Base
# ========================================================

@app.get("/")
def root():
    return {
        "message": "API on FastAPI is running with psycopg3",
        "status": "ok",
        "api": "API Energía — Gobierno del Estado",
        "version": "1.0.1"
    }

@app.get("/db")
def test_db():
    """
    Endpoint de prueba para verificar conexión a PostgreSQL
    """
    conninfo = (
        f"dbname={settings.DB_DATABASE} "
        f"user={settings.DB_USERNAME} "
        f"password={settings.DB_PASSWORD} "
        f"host={settings.DB_HOST} "
        f"port={settings.DB_PORT}"
    )

    try:
        # Con psycopg3, se maneja automáticamente el contexto
        with psycopg.connect(conninfo) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT NOW();")
                result = cur.fetchone()
        return {"status": "connected", "fecha_db": str(result[0])}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
# from fastapi import FastAPI
# import psycopg

# from app.core.config import settings
# from app.routers.prediccion_router import router as prediccion_router
# from fastapi.middleware.cors import CORSMiddleware

# from app.routers.analisis import router as analisis_router
# from app.routers.prediccion_router import router as prediccion_router
# from app.routers.catalogos import router as catalogos_router
# from app.routers.analisis_publico import router as analisisPublico_router

# app = FastAPI(
#     title="API Energía — Gobierno del Estado",
#     description="""
# API para análisis energético, histórico y predicción basada en consumo eléctrico.

# Incluye:
# - Análisis energético (consumo total, rankings, comparativas)
# - Predicción de consumo (SES + tendencia)
# - Simulaciones What-if
# """,
#     version="1.0.1"
# )


# # ========================================================
# # 📌 Registrar Routers (Versionado por API)
# # ========================================================
# app.include_router(analisis_router)
# app.include_router(prediccion_router)
# app.include_router(catalogos_router) 
# app.include_router(analisisPublico_router)


# # ========================================================
# # 🌐 CORS CONFIG
# # ========================================================
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Puedes restringir a tu dominio de producción
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )





# @app.get("/")
# def root():
#     return {"message": "API on FastAPI is running with psycopg3",
#             "status": "ok",
#             "api": "API Energía — Gobierno del Estado",
#             "version": "1.0.0"}

# @app.get("/db")
# def test_db():
#     """
#     Endpoint de prueba para verificar conexión a PostgreSQL
#     """
#     conninfo = (
#         f"dbname={settings.DB_DATABASE} "
#         f"user={settings.DB_USERNAME} "
#         f"password={settings.DB_PASSWORD} "
#         f"host={settings.DB_HOST} "
#         f"port={settings.DB_PORT}"
#     )

#     # Con psycopg3, se maneja automáticamente el contexto
#     with psycopg.connect(conninfo) as conn:
#         with conn.cursor() as cur:
#             cur.execute("SELECT NOW();")
#             result = cur.fetchone()

#     return {"fecha": str(result[0])}
