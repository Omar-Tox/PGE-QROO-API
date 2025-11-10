from fastapi import FastAPI
import psycopg
from app.routers import analisis
from app.core.config import settings

app = FastAPI(title="API Energética PGE-QROO")

# Registrar router principal
app.include_router(analisis.router)

@app.get("/")
def root():
    return {"message": "API on FastAPI is running with psycopg3"}

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
