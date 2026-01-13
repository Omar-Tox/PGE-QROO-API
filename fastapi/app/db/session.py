# app/db/session.py
# CONFIGURACIÓN ASÍNCRONA (Async)

import os
from dotenv import load_dotenv
# Importaciones asíncronas
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator

load_dotenv()

# ============================================================
# URL usando driver ASÍNCRONO (asyncpg)
# ============================================================
DATABASE_URL = (
    f"postgresql+asyncpg://{os.getenv('DB_USERNAME')}:"
    f"{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}"
)

# ============================================================
# Crear engine ASÍNCRONO
# ============================================================
async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

# ============================================================
# sessionmaker ASÍNCRONO
# ============================================================
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# ============================================================
# Dependencia ASÍNCRONA para FastAPI
# ============================================================
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependencia de FastAPI para obtener una sesión de DB asíncrona.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# # app/db/session.py

# import os
# from dotenv import load_dotenv
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

# load_dotenv()

# # ============================================================
# # URL usando psycopg3 (psycopg)
# # ============================================================
# DATABASE_URL = (
#     f"postgresql+psycopg://{os.getenv('DB_USERNAME')}:"
#     f"{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:"
#     f"{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}"
# )

# # ============================================================
# # Crear engine (SQLAlchemy 2.0+)
# # ============================================================
# engine = create_engine(
#     DATABASE_URL,
#     echo=False,
#     future=True
# )

# # ============================================================
# # sessionmaker para FastAPI
# # ============================================================
# SessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine
# )

# # ============================================================
# # Dependencia para FastAPI
# # ============================================================
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
