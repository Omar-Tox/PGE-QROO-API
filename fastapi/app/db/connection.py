
# app/db/connection.py
import os
import psycopg_pool
from dotenv import load_dotenv

load_dotenv()

# Configuración de conexión desde .env
DB_CONFIG = {
    "dbname": os.getenv("DB_DATABASE"),
    "user": os.getenv("DB_USERNAME"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

# Creamos un pool de conexiones
pool = psycopg_pool.ConnectionPool(
    conninfo=f"dbname={DB_CONFIG['dbname']} user={DB_CONFIG['user']} password={DB_CONFIG['password']} host={DB_CONFIG['host']} port={DB_CONFIG['port']}",
    min_size=1,
    max_size=5,
    timeout=10
)

def get_connection():
    """Obtiene una conexión del pool."""
    return pool.getconn()

def release_connection(conn):
    """Libera la conexión al pool."""
    pool.putconn(conn)


# import psycopg
# from app.core.config import settings

# def get_connection():
#     """
#     Retorna una conexión activa a PostgreSQL usando psycopg3.
#     """
#     conn = psycopg.connect(
#         dbname=settings.DB_DATABASE,
#         user=settings.DB_USERNAME,
#         password=settings.DB_PASSWORD,
#         host=settings.DB_HOST,
#         port=settings.DB_PORT
#     )
#     return conn
