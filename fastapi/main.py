from fastapi import FastAPI
import os
import psycopg2

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API on FastAPI is running"}

@app.get("/db")
def test_db():
    conn = psycopg2.connect(
        dbname = os.getenv("POSTGRES_DB"),
        user = os.getenv("POSTGRES_USER"),
        password = os.getenv("POSTGRES_PASSWORD"),
        host = "postgres"
    )
    cur = conn.cursor()
    cur.execute("SELECT NOW();")
    result = cur.fetchone()
    conn.close()
    return {"fecha: ": result[0]}