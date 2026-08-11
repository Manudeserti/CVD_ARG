import bcrypt

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