from fastapi import APIRouter, HTTPException,status
from database.database import get_db_connection
from schemas.institucion_schema import InstitucionCreate # <- Nueva importación

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

@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_institucion(institucion: InstitucionCreate):
    """
    Crea una nueva institución en la base de datos.
    """
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()
        
        # Inserción con RETURNING para que PostgreSQL nos devuelva el registro creado
        insert_query = """
            INSERT INTO instituciones (nombre, ciudad)
            VALUES (%s, %s)
            RETURNING id, nombre, ciudad, fecha_creacion;
        """
        
        # Ejecutamos pasando los datos validados por Pydantic
        cursor.execute(insert_query, (institucion.nombre, institucion.ciudad))
        nueva_inst = cursor.fetchone()
        
        # IMPORTANTE: Confirmamos la transacción para que se guarde de verdad
        conexion.commit()
        
        cursor.close()
        conexion.close()
        
        # Devolvemos el objeto recién creado
        return {
            "status": "success",
            "message": "Institución creada correctamente",
            "data": {
                "id": nueva_inst[0],
                "nombre": nueva_inst[1],
                "ciudad": nueva_inst[2],
                "fecha_creacion": nueva_inst[3]
            }
        }
        
    except Exception as e:
        # Si algo falla, deshacemos cualquier cambio a medias (Rollback)
        if 'conexion' in locals():
            conexion.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear: {str(e)}")