from fastapi import APIRouter, HTTPException
from database.database import get_db_connection

# Inicializamos el router para esta entidad
router = APIRouter(
    prefix="/api/instituciones",
    tags=["Instituciones"]
)

@router.get("/test-db")
def test_database_connection():
    """
    Endpoint para probar la conexión a la tabla instituciones.
    """
    try:
        # Usamos la función centralizada que creamos en database.py
        conexion = get_db_connection()
        cursor = conexion.cursor()
        
        # Ejecutamos la consulta
        cursor.execute("SELECT id, nombre, ciudad FROM instituciones LIMIT 5;")
        instituciones = cursor.fetchall()
        
        # Cerramos conexiones
        cursor.close()
        conexion.close()
        
        return {
            "status": "success",
            "message": "Conexión a Supabase exitosa desde el router",
            "data": instituciones
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error conectando a la BD: {str(e)}")