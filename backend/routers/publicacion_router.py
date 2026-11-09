import psycopg2
from fastapi import APIRouter, HTTPException, status, Depends, Query
from database.database import get_db_connection, error_interno
from schemas.publicacion_schema import PublicacionCreate, PublicacionResponse, FotoSubida
from utils import fotos
from utils.security import get_usuario_actual
from uuid import UUID
from typing import Optional

router = APIRouter(
    prefix="/api/publicaciones",
    tags=["Publicaciones"]
)

# --- ENDPOINT POST (Pedir URL para subir una foto) ---
@router.post("/fotos", status_code=status.HTTP_200_OK)
def pedir_url_de_foto(foto: FotoSubida, usuario_actual: dict = Depends(get_usuario_actual)):
    """
    Devuelve url_subida (el navegador hace PUT del archivo, con su Content-Type) y url_publica
    (se manda en imagenes_urls al crear la publicación).
    """
    try:
        return fotos.crear_url_subida(usuario_actual["id"], foto.tipo_archivo)
    except Exception as e:
        raise error_interno("El almacenamiento de fotos no respondió correctamente", 502)


# --- ENDPOINT POST (Crear publicación) ---
@router.post("/", response_model=PublicacionResponse, status_code=status.HTTP_201_CREATED)
def crear_publicacion(
    publicacion: PublicacionCreate, 
    usuario_actual: dict = Depends(get_usuario_actual)
):
    """
    Crea una nueva publicación en el Marketplace.
    Requiere un Token JWT válido. El vendedor_id se extrae automáticamente del token.
    """
    # --- VALIDACIONES DE NEGOCIO (Fail-Fast) ---
    if publicacion.tipo == 'venta' and publicacion.precio <= 0:
        raise HTTPException(
            status_code=400, 
            detail="Si el artículo es una venta, el precio debe ser mayor a 0."
        )
        
    if publicacion.tipo == 'donacion' and publicacion.precio > 0:
        raise HTTPException(
            status_code=400, 
            detail="Las donaciones no pueden tener un precio asignado."
        )

    if not all(fotos.es_foto_del_usuario(url, usuario_actual["id"]) for url in publicacion.imagenes_urls):
        raise HTTPException(status_code=400, detail="Alguna de las fotos no fue subida por este usuario.")

    conexion = None
    cursor = None

    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()
        
        vendedor_id = usuario_actual["id"]
        
        insert_query = """
            INSERT INTO publicaciones (
                vendedor_id, institucion_id, titulo, descripcion, 
                categoria, talle, tipo, precio, imagenes_urls
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, vendedor_id, institucion_id, titulo, descripcion, categoria, talle, tipo, precio, estado, imagenes_urls, fecha_publicacion;
        """
        
        cursor.execute(insert_query, (
            vendedor_id,
            publicacion.institucion_id,
            publicacion.titulo,
            publicacion.descripcion,
            publicacion.categoria,
            publicacion.talle,
            publicacion.tipo,
            publicacion.precio,
            publicacion.imagenes_urls
        ))
        
        nueva_pub = cursor.fetchone()
        conexion.commit()
        
        return {
            "id": nueva_pub[0], "vendedor_id": nueva_pub[1], "institucion_id": nueva_pub[2],
            "titulo": nueva_pub[3], "descripcion": nueva_pub[4], "categoria": nueva_pub[5],
            "talle": nueva_pub[6], "tipo": nueva_pub[7], "precio": nueva_pub[8],
            "estado": nueva_pub[9], "imagenes_urls": nueva_pub[10], "fecha_publicacion": nueva_pub[11]
        }
        
    except HTTPException:
        # Bypass para nuestros errores intencionales
        raise
    except psycopg2.errors.ForeignKeyViolation:
        conexion.rollback()
        raise HTTPException(status_code=400, detail="La institución indicada no existe")
    except Exception as e:
        # Solo hacemos rollback si la conexión llegó a abrirse
        if conexion:
            conexion.rollback()
        raise error_interno("Error al crear la publicación")
    finally:
        # Esto garantiza que la base de datos se cierre SIEMPRE
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


# --- ENDPOINT GET (Catálogo Público) ---
@router.get("/", response_model=list[PublicacionResponse], status_code=status.HTTP_200_OK)
def listar_publicaciones(
    provincia: Optional[str] = None,
    ciudad: Optional[str] = None,
    institucion_id: Optional[int] = None,
    categoria: Optional[str] = None,
    tipo: Optional[str] = None,
    talle: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Obtiene el catálogo de publicaciones disponibles, de a bloques (scroll infinito: offset = cantidad ya cargada).
    Todos los filtros son opcionales y se combinan (Provincia > Ciudad > Institución > Tipo de artículo).
    Ruta pública (no requiere Token).
    """
    conexion = None
    cursor = None

    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()

        # LEFT JOIN porque institucion_id es opcional: sin filtros de ubicación, esas publicaciones también aparecen
        query = """
            SELECT p.id, p.vendedor_id, p.institucion_id, p.titulo, p.descripcion,
                   p.categoria, p.talle, p.tipo, p.precio, p.estado, p.imagenes_urls, p.fecha_publicacion
            FROM publicaciones p
            LEFT JOIN instituciones i ON i.id = p.institucion_id
            WHERE p.estado = 'disponible'
              AND (%(provincia)s::text IS NULL OR i.provincia ILIKE %(provincia)s)
              AND (%(ciudad)s::text IS NULL OR i.ciudad ILIKE %(ciudad)s)
              AND (%(institucion_id)s::int IS NULL OR p.institucion_id = %(institucion_id)s)
              AND (%(categoria)s::text IS NULL OR p.categoria = %(categoria)s)
              AND (%(tipo)s::text IS NULL OR p.tipo = %(tipo)s)
              AND (%(talle)s::text IS NULL OR p.talle = %(talle)s)
            ORDER BY p.fecha_publicacion DESC, p.id
            LIMIT %(limit)s OFFSET %(offset)s;
        """
        cursor.execute(query, {
            "provincia": provincia, "ciudad": ciudad, "institucion_id": institucion_id,
            "categoria": categoria, "tipo": tipo, "talle": talle,
            "limit": limit, "offset": offset
        })
        publicaciones_db = cursor.fetchall()
        
        lista_publicaciones = []
        for pub in publicaciones_db:
            lista_publicaciones.append({
                "id": pub[0], "vendedor_id": pub[1], "institucion_id": pub[2],
                "titulo": pub[3], "descripcion": pub[4], "categoria": pub[5],
                "talle": pub[6], "tipo": pub[7], "precio": pub[8],
                "estado": pub[9], "imagenes_urls": pub[10], "fecha_publicacion": pub[11]
            })
            
        return lista_publicaciones
        
    except HTTPException:
        raise
    except Exception as e:
        raise error_interno("Error al obtener el catálogo")
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


# --- ENDPOINT GET (Mis publicaciones) ---
# Tiene que declararse antes de "/{id}", si no FastAPI intenta leer "mias" como un UUID
@router.get("/mias", response_model=list[PublicacionResponse], status_code=status.HTTP_200_OK)
def listar_mis_publicaciones(usuario_actual: dict = Depends(get_usuario_actual)):
    """
    Devuelve todas las publicaciones del usuario logueado, en cualquier estado salvo las dadas de baja.
    """
    conexion = None
    cursor = None

    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT id, vendedor_id, institucion_id, titulo, descripcion,
                   categoria, talle, tipo, precio, estado, imagenes_urls, fecha_publicacion
            FROM publicaciones
            WHERE vendedor_id = %s AND estado <> 'baja'
            ORDER BY fecha_publicacion DESC;
        """, (usuario_actual["id"],))

        return [
            {
                "id": pub[0], "vendedor_id": pub[1], "institucion_id": pub[2],
                "titulo": pub[3], "descripcion": pub[4], "categoria": pub[5],
                "talle": pub[6], "tipo": pub[7], "precio": pub[8],
                "estado": pub[9], "imagenes_urls": pub[10], "fecha_publicacion": pub[11]
            }
            for pub in cursor.fetchall()
        ]

    except Exception as e:
        raise error_interno("Error al obtener tus publicaciones")
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


# --- ENDPOINT DELETE (Dar de baja) ---
@router.delete("/{id}", status_code=status.HTTP_200_OK)
def dar_de_baja_publicacion(id: UUID, usuario_actual: dict = Depends(get_usuario_actual)):
    """
    Retira una publicación del catálogo. No se borra la fila para no perder el historial de transacciones.
    Solo el dueño puede hacerlo y solo si no hay una operación en curso.
    """
    conexion = None
    cursor = None

    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()

        cursor.execute("SELECT vendedor_id, estado FROM publicaciones WHERE id = %s FOR UPDATE;", (str(id),))
        pub = cursor.fetchone()

        if not pub:
            raise HTTPException(status_code=404, detail="Publicación no encontrada")

        vendedor_id, estado_actual = pub

        if str(vendedor_id) != str(usuario_actual["id"]):
            raise HTTPException(status_code=403, detail="Solo el dueño puede dar de baja esta publicación")

        if estado_actual != 'disponible':
            raise HTTPException(
                status_code=400,
                detail=f"No se puede dar de baja una publicación en estado '{estado_actual}'"
            )

        cursor.execute("UPDATE publicaciones SET estado = 'baja' WHERE id = %s;", (str(id),))
        conexion.commit()

        return {"status": "success", "message": "Publicación dada de baja"}

    except HTTPException:
        if conexion:
            conexion.rollback()
        raise
    except Exception as e:
        if conexion:
            conexion.rollback()
        raise error_interno("Error al dar de baja")
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


# --- ENDPOINT GET (Detalle de un artículo) ---
@router.get("/{id}", response_model=PublicacionResponse, status_code=status.HTTP_200_OK)
def obtener_publicacion_por_id(id: UUID):
    """
    Busca una publicación específica por su ID.
    Ruta pública.
    """
    conexion = None
    cursor = None

    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()
        
        query = """
            SELECT id, vendedor_id, institucion_id, titulo, descripcion, 
                   categoria, talle, tipo, precio, estado, imagenes_urls, fecha_publicacion 
            FROM publicaciones 
            WHERE id = %s;
        """
        cursor.execute(query, (str(id),))
        pub = cursor.fetchone()
        
        if not pub:
            # Disparamos un error 404 intencional
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Publicación no encontrada"
            )
            
        return {
            "id": pub[0], "vendedor_id": pub[1], "institucion_id": pub[2],
            "titulo": pub[3], "descripcion": pub[4], "categoria": pub[5],
            "talle": pub[6], "tipo": pub[7], "precio": pub[8],
            "estado": pub[9], "imagenes_urls": pub[10], "fecha_publicacion": pub[11]
        }
        
    except HTTPException:
        # Este bypass es fundamental acá para que el frontend reciba el 404 y no un 500
        raise
    except Exception as e:
        raise error_interno("Error al buscar la publicación")
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()