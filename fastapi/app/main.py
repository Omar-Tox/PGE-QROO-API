from fastapi import FastAPI
import psycopg

from app.core.config import settings
from app.routers.prediccion_router import router as prediccion_router
from fastapi.middleware.cors import CORSMiddleware

from app.routers.analisis import router as analisis_router
from app.routers.prediccion_router import router as prediccion_router


app = FastAPI(
    title="API Energía — Gobierno del Estado",
    description="""
API para análisis energético, histórico y predicción basada en consumo eléctrico.

Incluye:
- Análisis energético (consumo total, rankings, comparativas)
- Predicción de consumo (SES + tendencia)
- Simulaciones What-if
""",
    version="1.0.0"
)


# ========================================================
# 📌 Registrar Routers (Versionado por API)
# ========================================================
app.include_router(analisis_router, prefix="/v1")
app.include_router(prediccion_router, prefix="/v1")



# ========================================================
# 🌐 CORS CONFIG
# ========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes restringir a tu dominio de producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





@app.get("/")
def root():
    return {"message": "API on FastAPI is running with psycopg3",
            "status": "ok",
            "api": "API Energía — Gobierno del Estado",
            "version": "1.0.0"}

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

    # Con psycopg3, se maneja automáticamente el contexto
    with psycopg.connect(conninfo) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT NOW();")
            result = cur.fetchone()

    return {"fecha": str(result[0])}
