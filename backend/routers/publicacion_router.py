from fastapi import APIRouter, HTTPException, status, Depends
from database.database import get_db_connection
from schemas.publicacion_schema import PublicacionCreate, PublicacionResponse
from utils.security import get_usuario_actual
from uuid import UUID

router = APIRouter(
    prefix="/api/publicaciones",
    tags=["Publicaciones"]
)

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
    except Exception as e:
        # Solo hacemos rollback si la conexión llegó a abrirse
        if conexion:
            conexion.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear la publicación: {str(e)}")
    finally:
        # Esto garantiza que la base de datos se cierre SIEMPRE
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


# --- ENDPOINT GET (Catálogo Público) ---
@router.get("/", response_model=list[PublicacionResponse], status_code=status.HTTP_200_OK)
def listar_publicaciones():
    """
    Obtiene el catálogo completo de publicaciones disponibles.
    Ruta pública (no requiere Token).
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
            ORDER BY fecha_publicacion DESC;
        """
        cursor.execute(query)
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
        raise HTTPException(status_code=500, detail=f"Error al obtener el catálogo: {str(e)}")
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
        raise HTTPException(status_code=500, detail=f"Error al buscar la publicación: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()