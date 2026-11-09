import psycopg2
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional
from uuid import UUID
from database.database import get_db_connection, error_interno
from schemas.institucion_schema import InstitucionCreate, InstitucionResponse, SolicitudResolucion
from utils.security import requerir_admin

# Inicializamos el router para esta entidad
router = APIRouter(
    prefix="/api/instituciones",
    tags=["Instituciones"]
)

# --- ENDPOINT GET (Listado público para los filtros del catálogo) ---
@router.get("/", response_model=list[InstitucionResponse], status_code=status.HTTP_200_OK)
def listar_instituciones(provincia: Optional[str] = None, ciudad: Optional[str] = None):
    """
    Lista las instituciones, opcionalmente filtradas por provincia y/o ciudad.
    Alimenta los filtros en cascada Provincia > Ciudad > Institución del frontend.
    """
    conexion = None
    cursor = None

    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()

        # Cada filtro es opcional: si viene en NULL, la condición se cumple siempre
        cursor.execute("""
            SELECT id, nombre, ciudad, provincia, fecha_creacion
            FROM instituciones
            WHERE (%(provincia)s::text IS NULL OR provincia ILIKE %(provincia)s)
              AND (%(ciudad)s::text IS NULL OR ciudad ILIKE %(ciudad)s)
            ORDER BY provincia, ciudad, nombre;
        """, {"provincia": provincia, "ciudad": ciudad})

        return [
            {"id": i[0], "nombre": i[1], "ciudad": i[2], "provincia": i[3], "fecha_creacion": i[4]}
            for i in cursor.fetchall()
        ]

    except Exception as e:
        raise error_interno("Error al listar instituciones")
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


@router.get("/solicitudes", status_code=status.HTTP_200_OK, dependencies=[Depends(requerir_admin)])
def listar_solicitudes():
    """
    Solicitudes de alta de colegios que esperan una resolución, de la más antigua a la más nueva.
    """
    conexion = None
    cursor = None

    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT s.id, s.nombre, s.ciudad, s.provincia, s.fecha_creacion, p.id, p.titulo
            FROM solicitudes_institucion s
            JOIN publicaciones p ON p.id = s.publicacion_id
            WHERE s.estado = 'pendiente'
            ORDER BY s.fecha_creacion;
        """)

        return [
            {"id": s[0], "nombre": s[1], "ciudad": s[2], "provincia": s[3], "fecha_creacion": s[4],
             "publicacion_id": s[5], "publicacion_titulo": s[6]}
            for s in cursor.fetchall()
        ]

    except Exception as e:
        raise error_interno("Error al listar las solicitudes")
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


@router.post("/solicitudes/{id}/resolver", status_code=status.HTTP_200_OK, dependencies=[Depends(requerir_admin)])
def resolver_solicitud(id: UUID, resolucion: SolicitudResolucion):
    """
    aceptada: crea el colegio y publica el artículo.
    duplicada: el colegio ya existía; se le asigna ese y se publica, avisando al dueño con cuál quedó.
    rechazada: el colegio no existe; la publicación queda en borrador para que el dueño elija otro.
    """
    if resolucion.resultado == 'duplicada' and resolucion.institucion_id is None:
        raise HTTPException(status_code=400, detail="Indicá cuál es el colegio correcto.")

    conexion = None
    cursor = None

    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()

        # El bloqueo evita resolver dos veces la misma solicitud si se aprieta dos veces
        cursor.execute("""
            SELECT publicacion_id, nombre, ciudad, provincia, estado
            FROM solicitudes_institucion WHERE id = %s FOR UPDATE;
        """, (str(id),))
        solicitud = cursor.fetchone()

        if not solicitud:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")

        publicacion_id, nombre, ciudad, provincia, estado = solicitud

        if estado != 'pendiente':
            raise HTTPException(status_code=409, detail="La solicitud ya fue resuelta")

        # Solo se toca la publicación si sigue esperando: su dueño pudo haberla dado de baja mientras tanto
        if resolucion.resultado == 'rechazada':
            cursor.execute("""
                UPDATE publicaciones SET estado = 'borrador', aviso = %s
                WHERE id = %s AND estado = 'pendiente_colegio';
            """, (f'No pudimos dar de alta "{nombre}". Elegí otro colegio para publicar tu artículo.', str(publicacion_id)))
        else:
            if resolucion.resultado == 'aceptada':
                cursor.execute("""
                    INSERT INTO instituciones (nombre, ciudad, provincia) VALUES (%s, %s, %s) RETURNING id;
                """, (nombre, ciudad, provincia))
                institucion_id = cursor.fetchone()[0]
                aviso = None
            else:
                institucion_id = resolucion.institucion_id
                cursor.execute("SELECT nombre FROM instituciones WHERE id = %s;", (institucion_id,))
                existente = cursor.fetchone()
                if not existente:
                    raise HTTPException(status_code=400, detail="El colegio indicado no existe")
                aviso = f'Tu publicación ya está activa con el colegio "{existente[0]}".'

            cursor.execute("""
                UPDATE publicaciones
                SET institucion_id = %s, estado = 'disponible', aviso = %s, fecha_publicacion = now()
                WHERE id = %s AND estado = 'pendiente_colegio';
            """, (institucion_id, aviso, str(publicacion_id)))

        cursor.execute("UPDATE solicitudes_institucion SET estado = %s WHERE id = %s;", (resolucion.resultado, str(id)))
        conexion.commit()

        return {"status": "success", "message": "Solicitud resuelta"}

    except HTTPException:
        if conexion:
            conexion.rollback()
        raise
    except Exception as e:
        if conexion:
            conexion.rollback()
        raise error_interno("Error al resolver la solicitud")
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(requerir_admin)])
def crear_institucion(institucion: InstitucionCreate):
    """
    Crea una nueva institución en la base de datos.
    """
    conexion = None
    cursor = None

    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()
        
        # Inserción con RETURNING para que PostgreSQL nos devuelva el registro creado
        insert_query = """
            INSERT INTO instituciones (nombre, ciudad, provincia)
            VALUES (%s, %s, %s)
            RETURNING id, nombre, ciudad, provincia, fecha_creacion;
        """
        
        # Ejecutamos pasando los datos validados por Pydantic
        cursor.execute(insert_query, (
            institucion.nombre,
            institucion.ciudad,
            institucion.provincia
        ))
        nueva_inst = cursor.fetchone()
        
        # IMPORTANTE: Confirmamos la transacción para que se guarde de verdad
        conexion.commit()
        
        
        # Devolvemos el objeto recién creado
        return {
            "status": "success",
            "message": "Institución creada correctamente",
            "data": {
                "id": nueva_inst[0],
                "nombre": nueva_inst[1],
                "ciudad": nueva_inst[2],
                "provincia": nueva_inst[3],
                "fecha_creacion": nueva_inst[4]
            }
        }
        
    except Exception as e:
        # Si algo falla, deshacemos cualquier cambio a medias (Rollback)
        if conexion:
            conexion.rollback()
        raise error_interno("Error al crear")
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()
    

    # --- ENDPOINT PUT (Editar) ---
@router.put("/{id}", status_code=status.HTTP_200_OK, dependencies=[Depends(requerir_admin)])
def actualizar_institucion(id: int, institucion: InstitucionCreate):
    """
    Actualiza el nombre, la ciudad o la provincia de una institución existente.
    """
    conexion = None
    cursor = None

    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()

        # El UPDATE también puede usar RETURNING para confirmar los datos guardados
        update_query = """
            UPDATE instituciones
            SET nombre = %s, ciudad = %s, provincia = %s
            WHERE id = %s
            RETURNING id, nombre, ciudad, provincia, fecha_creacion;
        """

        cursor.execute(update_query, (institucion.nombre, institucion.ciudad, institucion.provincia, id))
        inst_actualizada = cursor.fetchone()
        
        # Si el ID no existe en la base de datos, fetchone() devuelve None
        if not inst_actualizada:
            conexion.rollback()
            raise HTTPException(status_code=404, detail="Institución no encontrada")
            
        conexion.commit()
        
        return {
            "status": "success",
            "message": "Institución actualizada correctamente",
            "data": {
                "id": inst_actualizada[0],
                "nombre": inst_actualizada[1],
                "ciudad": inst_actualizada[2],
                "provincia": inst_actualizada[3],
                "fecha_creacion": inst_actualizada[4]
            }
        }
        
    except HTTPException:
        # Esto es para que FastAPI no pise el error 404 que lanzamos arriba
        raise
    except Exception as e:
        if conexion:
            conexion.rollback()
        raise error_interno("Error al actualizar")
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


# --- ENDPOINT DELETE (Borrar) ---
@router.delete("/{id}", status_code=status.HTTP_200_OK, dependencies=[Depends(requerir_admin)])
def eliminar_institucion(id: int):
    """
    Elimina permanentemente una institución por su ID.
    """
    conexion = None
    cursor = None

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
        
        return {
            "status": "success",
            "message": f"Institución con ID {id} eliminada con éxito"
        }
        
    except HTTPException:
        raise
    except psycopg2.errors.ForeignKeyViolation:
        conexion.rollback()
        raise HTTPException(status_code=409, detail="La institución tiene publicaciones asociadas")
    except Exception as e:
        if conexion:
            conexion.rollback()
        raise error_interno("Error al eliminar")
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()
