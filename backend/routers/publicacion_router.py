from fastapi import APIRouter, HTTPException, status, Depends
from database.database import get_db_connection
from schemas.publicacion_schema import PublicacionCreate, PublicacionResponse
from utils.security import obtener_usuario_actual
from uuid import UUID

router = APIRouter(
    prefix="/api/publicaciones",
    tags=["Publicaciones"]
)

@router.post("/", response_model=PublicacionResponse, status_code=status.HTTP_201_CREATED)
def crear_publicacion(
    publicacion: PublicacionCreate, 
    usuario_actual: dict = Depends(obtener_usuario_actual) # <- ¡Acá está el guardia de seguridad!
):
    """
    Crea una nueva publicación en el Marketplace.
    Requiere un Token JWT válido. El vendedor_id se extrae automáticamente del token.
    """
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()
        
        # 1. Extraemos el ID del vendedor desde el token desencriptado
        vendedor_id = usuario_actual["id"]
        
        # 2. Preparamos el INSERT con los nuevos campos de categoría y talle
        insert_query = """
            INSERT INTO publicaciones (
                vendedor_id, institucion_id, titulo, descripcion, 
                categoria, talle, tipo, precio, imagenes_urls
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, vendedor_id, institucion_id, titulo, descripcion, categoria, talle, tipo, precio, estado, imagenes_urls, fecha_publicacion;
        """
        
        # 3. Ejecutamos la consulta
        cursor.execute(insert_query, (
            vendedor_id,
            publicacion.institucion_id, # Puede ser null
            publicacion.titulo,
            publicacion.descripcion,
            publicacion.categoria,
            publicacion.talle, # Puede ser null
            publicacion.tipo,
            publicacion.precio,
            publicacion.imagenes_urls
        ))
        
        nueva_pub = cursor.fetchone()
        conexion.commit()
        
        cursor.close()
        conexion.close()
        
        # 4. Empaquetamos la respuesta para que Pydantic la filtre y valide
        return {
            "id": nueva_pub[0],
            "vendedor_id": nueva_pub[1],
            "institucion_id": nueva_pub[2],
            "titulo": nueva_pub[3],
            "descripcion": nueva_pub[4],
            "categoria": nueva_pub[5],
            "talle": nueva_pub[6],
            "tipo": nueva_pub[7],
            "precio": nueva_pub[8],
            "estado": nueva_pub[9],
            "imagenes_urls": nueva_pub[10],
            "fecha_publicacion": nueva_pub[11]
        }
        
    except Exception as e:
        if 'conexion' in locals():
            conexion.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear la publicación: {str(e)}")


# --- ENDPOINT GET (Catálogo Público) ---
@router.get("/", response_model=list[PublicacionResponse], status_code=status.HTTP_200_OK)
def listar_publicaciones():
    """
    Obtiene el catálogo completo de publicaciones disponibles.
    Esta ruta es pública (no requiere Token) para que cualquier persona pueda ver la vidriera.
    """
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()
        
        # Buscamos todas las publicaciones, ordenadas para que las más nuevas salgan primero
        query = """
            SELECT id, vendedor_id, institucion_id, titulo, descripcion, 
                   categoria, talle, tipo, precio, estado, imagenes_urls, fecha_publicacion 
            FROM publicaciones 
            ORDER BY fecha_publicacion DESC;
        """
        cursor.execute(query)
        publicaciones_db = cursor.fetchall()
        
        cursor.close()
        conexion.close()
        
        # Transformamos las filas crudas de SQL en una lista de diccionarios para Pydantic
        lista_publicaciones = []
        for pub in publicaciones_db:
            lista_publicaciones.append({
                "id": pub[0],
                "vendedor_id": pub[1],
                "institucion_id": pub[2],
                "titulo": pub[3],
                "descripcion": pub[4],
                "categoria": pub[5],
                "talle": pub[6],
                "tipo": pub[7],
                "precio": pub[8],
                "estado": pub[9],
                "imagenes_urls": pub[10],
                "fecha_publicacion": pub[11]
            })
            
        return lista_publicaciones
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el catálogo: {str(e)}")


# --- ENDPOINT GET (Detalle de un artículo) ---
@router.get("/{id}", response_model=PublicacionResponse, status_code=status.HTTP_200_OK)
def obtener_publicacion_por_id(id: UUID):
    """
    Busca una publicación específica por su ID.
    Ruta pública.
    """
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()
        
        # Buscamos la publicación puntual. Al UUID lo convertimos a string para que PostgreSQL lo entienda perfecto.
        query = """
            SELECT id, vendedor_id, institucion_id, titulo, descripcion, 
                   categoria, talle, tipo, precio, estado, imagenes_urls, fecha_publicacion 
            FROM publicaciones 
            WHERE id = %s;
        """
        cursor.execute(query, (str(id),))
        pub = cursor.fetchone()
        
        cursor.close()
        conexion.close()
        
        # Si la consulta no devuelve nada, el artículo no existe o fue borrado
        if not pub:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Publicación no encontrada"
            )
            
        # Si existe, armamos el diccionario para devolverlo
        return {
            "id": pub[0],
            "vendedor_id": pub[1],
            "institucion_id": pub[2],
            "titulo": pub[3],
            "descripcion": pub[4],
            "categoria": pub[5],
            "talle": pub[6],
            "tipo": pub[7],
            "precio": pub[8],
            "estado": pub[9],
            "imagenes_urls": pub[10],
            "fecha_publicacion": pub[11]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al buscar la publicación: {str(e)}")