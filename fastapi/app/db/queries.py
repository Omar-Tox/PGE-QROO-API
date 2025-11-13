# app/db/queries.py
from app.db.connection import get_connection, release_connection
from app.models.consumo_historico import ConsumoHistorico
from app.models.presupuestos import Presupuesto

def obtener_consumo_total(anio: int, id_sector: int = None, id_dependencia: int = None):
    query = """
        SELECT 
            s.nombre_sector, 
            d.nombre_dependencia, 
            SUM(c.consumo_kwh) AS total_kwh, 
            SUM(c.costo_total) AS total_costo
        FROM consumo_historico c
        JOIN edificio e ON c.id_edificio = e.id_edificio
        JOIN dependencias d ON e.id_dependencia = d.id_dependencia
        JOIN sector s ON d.id_sector = s.id_sector
        WHERE c.anio = %s
    """
    params = [anio]

    if id_sector:
        query += " AND s.id_sector = %s"
        params.append(id_sector)
    if id_dependencia:
        query += " AND d.id_dependencia = %s"
        params.append(id_dependencia)

    query += """
        GROUP BY s.nombre_sector, d.nombre_dependencia
        ORDER BY total_kwh DESC;
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, tuple(params))
            return cur.fetchall()
    finally:
        release_connection(conn)
        
def obtener_consumo_historico(anio: int):
    query = """
        SELECT 
            id, id_edificio, anio, mes, consumo_kwh, costo_total, fuente_dato, fecha_registro
        FROM consumo_historico
        WHERE anio = %s
        ORDER BY mes;
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, (anio,))
            rows = cur.fetchall()
        return [
            ConsumoHistorico(
                id=row[0],
                id_edificio=row[1],
                anio=row[2],
                mes=row[3],
                consumo_kwh=row[4],
                costo_total=row[5],
                fuente_dato=row[6],
                fecha_registro=row[7]
            ) for row in rows
        ]
    finally:
        release_connection(conn)