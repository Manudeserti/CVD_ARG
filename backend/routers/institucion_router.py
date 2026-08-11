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

    # --- ENDPOINT PUT (Editar) ---
@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_institucion(id: int, institucion: InstitucionCreate):
    """
    Actualiza el nombre o la ciudad de una institución existente.
    """
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()
        
        # El UPDATE también puede usar RETURNING para confirmar los datos guardados
        update_query = """
            UPDATE instituciones 
            SET nombre = %s, ciudad = %s 
            WHERE id = %s 
            RETURNING id, nombre, ciudad, fecha_creacion;
        """
        
        cursor.execute(update_query, (institucion.nombre, institucion.ciudad, id))
        inst_actualizada = cursor.fetchone()
        
        # Si el ID no existe en la base de datos, fetchone() devuelve None
        if not inst_actualizada:
            conexion.rollback()
            raise HTTPException(status_code=404, detail="Institución no encontrada")
            
        conexion.commit()
        cursor.close()
        conexion.close()
        
        return {
            "status": "success",
            "message": "Institución actualizada correctamente",
            "data": {
                "id": inst_actualizada[0],
                "nombre": inst_actualizada[1],
                "ciudad": inst_actualizada[2],
                "fecha_creacion": inst_actualizada[3]
            }
        }
        
    except HTTPException:
        # Esto es para que FastAPI no pise el error 404 que lanzamos arriba
        raise
    except Exception as e:
        if 'conexion' in locals():
            conexion.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar: {str(e)}")


# --- ENDPOINT DELETE (Borrar) ---
@router.delete("/{id}", status_code=status.HTTP_200_OK)
def eliminar_institucion(id: int):
    """
    Elimina permanentemente una institución por su ID.
    """
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()
        
        delete_query = "DELETE FROM instituciones WHERE id = %s RETURNING id;"
        
        cursor.execute(delete_query, (id,))
        inst_eliminada = cursor.fetchone()
        
        if not inst_eliminada:
            conexion.rollback()
            raise HTTPException(status_code=404, detail="Institución no encontrada")
            
        conexion.commit()
        cursor.close()
        conexion.close()
        
        return {
            "status": "success",
            "message": f"Institución con ID {id} eliminada con éxito"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if 'conexion' in locals():
            conexion.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar: {str(e)}")