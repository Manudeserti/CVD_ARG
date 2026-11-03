import logging
import psycopg2
import os
from dotenv import load_dotenv
from fastapi import HTTPException

# Cargamos las variables de entorno una sola vez
load_dotenv()

def get_db_connection():
    """
    Establece y devuelve una conexión a la base de datos PostgreSQL en Supabase.
    """
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def error_interno(mensaje: str, status_code: int = 500) -> HTTPException:
    """
    Se llama dentro de un except: registra el error completo en los logs (Vercel → Logs)
    y devuelve un error con un mensaje genérico, sin detalles internos para el cliente.
    """
    logging.getLogger("cvd").exception(mensaje)
    return HTTPException(status_code=status_code, detail=mensaje)
