from fastapi import APIRouter, HTTPException, status, Depends
from database.database import get_db_connection
from schemas.usuario_schema import UsuarioCreate, UsuarioResponse, UsuarioLogin
from utils.security import hash_password, verify_password, crear_token_acceso, get_usuario_actual

router = APIRouter(
    prefix="/api/usuarios",
    tags=["Usuarios"]
)

# --- ENDPOINT POST (Registro) ---
@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(usuario: UsuarioCreate):
    """
    Registra un nuevo usuario en la plataforma. 
    La contraseña se encripta automáticamente con bcrypt.
    """
    conexion = None
    cursor = None
    
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()
        
        # 1. Encriptamos la contraseña en texto plano que nos manda Pydantic
        hashed_pwd = hash_password(usuario.password)
        
        # 2. Preparamos el INSERT
        insert_query = """
            INSERT INTO usuarios (email, nombre, apellido, password_hash, telefono)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, email, nombre, apellido, telefono, rol, fecha_registro;
        """
        
        # 3. Ejecutamos enviando la clave ya encriptada
        cursor.execute(insert_query, (
            usuario.email, 
            usuario.nombre,
            usuario.apellido, 
            hashed_pwd, 
            usuario.telefono
        ))
        
        nuevo_usuario = cursor.fetchone()
        conexion.commit()
        
        # 4. Devolvemos los datos en un diccionario que coincide con nuestro UsuarioResponse
        return {
            "id": nuevo_usuario[0],
            "email": nuevo_usuario[1],
            "nombre": nuevo_usuario[2],
            "apellido": nuevo_usuario[3],
            "telefono": nuevo_usuario[4],
            "rol": nuevo_usuario[5],
            "fecha_registro": nuevo_usuario[6]
        }
        
    except Exception as e:
        if conexion:
            conexion.rollback()
            
        # Si el error menciona "unique constraint", es porque el mail ya existe
        if "unique constraint" in str(e).lower() or "UniqueViolation" in str(type(e).__name__):
            raise HTTPException(status_code=400, detail="Este correo electrónico ya está registrado.")
            
        raise HTTPException(status_code=500, detail=f"Error al registrar usuario: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


# --- ENDPOINT POST (Login) ---
@router.post("/login", status_code=status.HTTP_200_OK)
def login_usuario(credenciales: UsuarioLogin):
    """
    Verifica las credenciales y, si son válidas, devuelve un Token JWT de acceso.
    """
    conexion = None
    cursor = None
    
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()
        
        # Cambiamos nombre_completo por nombre, apellido
        query = "SELECT id, email, nombre, apellido, password_hash, rol FROM usuarios WHERE email = %s;"
        cursor.execute(query, (credenciales.email,))
        usuario_db = cursor.fetchone()
        
        if not usuario_db:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")
            
        # ¡Ojo acá! El índice de password_hash se movió a [4]
        hash_guardado = usuario_db[4]
        clave_correcta = verify_password(credenciales.password, hash_guardado)
        
        if not clave_correcta:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")
            
        # 1. Elegimos qué datos queremos "guardar" adentro del token
        # El rol también se movió, ahora es el índice [5]
        token_data = {
            "sub": credenciales.email,
            "id": str(usuario_db[0]),
            "rol": usuario_db[5]
        }
        
        # 2. Fabricamos el token
        token = crear_token_acceso(token_data)
        
        # 3. Devolvemos la respuesta usando el formato OAuth2
        return {
            "access_token": token,
            "token_type": "bearer",
            "usuario": {
                "id": usuario_db[0],
                "nombre": usuario_db[2],
                "apellido": usuario_db[3],
                "rol": usuario_db[5]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


# --- ENDPOINT GET (Perfil Privado) ---
@router.get("/mi-perfil", status_code=status.HTTP_200_OK)
def ver_perfil_privado(usuario_actual: dict = Depends(get_usuario_actual)):
    """
    Ruta protegida. Solo se puede acceder con un Token JWT válido.
    """
    # Como el token solo guarda sub (email), id y rol, no hace falta tocar nada acá.
    return {
        "status": "success",
        "message": "¡Lograste pasar el control de seguridad!",
        "datos_del_token": usuario_actual
    }