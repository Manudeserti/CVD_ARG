from fastapi import APIRouter, HTTPException, status
from database.database import get_db_connection
from schemas.usuario_schema import UsuarioCreate, UsuarioResponse, UsuarioLogin
from utils.security import hash_password, verify_password

router = APIRouter(
    prefix="/api/usuarios",
    tags=["Usuarios"]
)

# Magia de FastAPI: Usamos response_model=UsuarioResponse para que filtre la contraseña de la respuesta
@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(usuario: UsuarioCreate):
    """
    Registra un nuevo usuario en la plataforma. 
    La contraseña se encripta automáticamente con bcrypt.
    """
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()
        
        # 1. Encriptamos la contraseña en texto plano que nos manda Pydantic
        hashed_pwd = hash_password(usuario.password)
        
        # 2. Preparamos el INSERT
        insert_query = """
            INSERT INTO usuarios (email, nombre_completo, password_hash, telefono)
            VALUES (%s, %s, %s, %s)
            RETURNING id, email, nombre_completo, telefono, rol, fecha_registro;
        """
        
        # 3. Ejecutamos enviando la clave ya encriptada
        cursor.execute(insert_query, (
            usuario.email, 
            usuario.nombre_completo, 
            hashed_pwd, 
            usuario.telefono
        ))
        
        nuevo_usuario = cursor.fetchone()
        conexion.commit()
        
        cursor.close()
        conexion.close()
        
        # 4. Devolvemos los datos en un diccionario que coincide con nuestro UsuarioResponse
        return {
            "id": nuevo_usuario[0],
            "email": nuevo_usuario[1],
            "nombre_completo": nuevo_usuario[2],
            "telefono": nuevo_usuario[3],
            "rol": nuevo_usuario[4],
            "fecha_registro": nuevo_usuario[5]
        }
        
    except Exception as e:
        if 'conexion' in locals():
            conexion.rollback()
            
        # Si el error menciona "unique constraint", es porque el mail ya existe
        if "unique constraint" in str(e).lower() or "UniqueViolation" in str(type(e).__name__):
            raise HTTPException(status_code=400, detail="Este correo electrónico ya está registrado.")
            
        raise HTTPException(status_code=500, detail=f"Error al registrar usuario: {str(e)}")


# --- ENDPOINT POST (Login) ---
@router.post("/login", status_code=status.HTTP_200_OK)
def login_usuario(credenciales: UsuarioLogin):
    """
    Verifica las credenciales de un usuario.
    Si son correctas, devuelve los datos básicos (próximamente devolverá un Token JWT).
    """
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()
        
        # 1. Buscamos al usuario por su email
        query = "SELECT id, email, nombre_completo, password_hash, rol FROM usuarios WHERE email = %s;"
        cursor.execute(query, (credenciales.email,))
        usuario_db = cursor.fetchone()
        
        cursor.close()
        conexion.close()
        
        # 2. Si la base de datos devuelve None, el email no existe
        # (Por seguridad, siempre decimos "Credenciales incorrectas" para no avivar a los hackers de qué correos existen en nuestra BD)
        if not usuario_db:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")
            
        # 3. La prueba de fuego: Comparamos la clave tipeada con el hash guardado
        hash_guardado = usuario_db[3]
        clave_correcta = verify_password(credenciales.password, hash_guardado)
        
        if not clave_correcta:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")
            
        # 4. ¡Acceso concedido! 
        return {
            "status": "success",
            "message": f"¡Bienvenido de nuevo, {usuario_db[2]}!",
            "data": {
                "id": usuario_db[0],
                "email": usuario_db[1],
                "nombre_completo": usuario_db[2],
                "rol": usuario_db[4]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")