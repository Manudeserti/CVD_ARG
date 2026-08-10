import psycopg2
import os
from dotenv import load_dotenv

# Cargamos las variables de entorno una sola vez
load_dotenv()

def get_db_connection():
    """
    Establece y devuelve una conexión a la base de datos PostgreSQL en Supabase.
    """
    return psycopg2.connect(os.getenv("DATABASE_URL"))