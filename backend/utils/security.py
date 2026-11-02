import bcrypt
import hmac
import jwt
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


load_dotenv()

def hash_password(password: str) -> str:
    """
    Toma una contraseña en texto plano, genera una 'sal' matemática 
    y devuelve el hash encriptado de forma nativa.
    """
    # 1. Bcrypt requiere que el texto puro se convierta a bytes
    pwd_bytes = password.encode('utf-8')
    
    # 2. Generamos la Sal y creamos el hash
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    
    # 3. Lo decodificamos a texto (str) para que PostgreSQL lo guarde sin problemas
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compara la contraseña que el usuario escribe al hacer Login 
    con el hash indescifrable que tenemos en la base de datos.
    """
    # Convertimos ambos textos a bytes para que bcrypt los pueda procesar
    password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)


# Sin valor por defecto: si falta en el .env, el servidor no arranca (mejor que firmar tokens con una clave conocida)
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120


def crear_token_acceso(data: dict) -> str:
    """
    Toma los datos básicos del usuario (ej: ID y Rol), les agrega una fecha de 
    vencimiento, y los firma digitalmente creando el Token JWT.
    """
    # Hacemos una copia de los datos para no modificar el diccionario original
    to_encode = data.copy()
    
    # Calculamos la fecha y hora exacta de expiración (Hora actual + 2 horas)
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Agregamos la fecha de expiración ("exp" es una convención estándar de JWT)
    to_encode.update({"exp": expire})
    
    # Generamos el token final sellado con nuestra clave secreta
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


# Le avisamos a FastAPI que vamos a usar tokens tipo "Bearer" (el estándar)
# Esto además hace que en Swagger aparezca mágicamente un botón verde de "Authorize"
seguridad_token = HTTPBearer()

def get_usuario_actual(credenciales: HTTPAuthorizationCredentials = Depends(seguridad_token)):
    """
    Intercepta la request, extrae el JWT, 
    verifica su firma y devuelve los datos del usuario.
    """
    token = credenciales.credentials
    
    try:
        # Intentamos decodificar el token usando tu súper clave  .env
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Si todo sale bien, devolvemos los datos (ID, email, rol) que estaban adentro
        return payload
        
    except jwt.ExpiredSignatureError:
        # Si pasaron las 2 horas, el token caducó
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="El token ha expirado. Por favor, iniciá sesión de nuevo."
        )
    except jwt.InvalidTokenError:
        # Si alguien alteró el token o está mal formado
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas o token alterado."
        )


def requerir_cron(credenciales: HTTPAuthorizationCredentials = Depends(seguridad_token)):
    """
    Autoriza las tareas programadas de Vercel Cron, que envían "Authorization: Bearer <CRON_SECRET>".
    """
    secreto = os.getenv("CRON_SECRET")
    if not secreto or not hmac.compare_digest(credenciales.credentials, secreto):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo las tareas programadas pueden ejecutar esta acción."
        )


def requerir_admin(usuario_actual: dict = Depends(get_usuario_actual)):
    """
    Igual que get_usuario_actual, pero además exige rol 'admin'.
    """
    if usuario_actual.get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta acción requiere permisos de administrador."
        )
    return usuario_actual