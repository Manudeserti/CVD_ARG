from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

# 1. Molde Base:  datos que comparten la creación y la respuesta
class UsuarioBase(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico válido")
    nombre_completo: str = Field(..., min_length=3, max_length=150)
    telefono: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto opcional")

# 2. Molde de Entrada: Lo que pone alguien que se registra
class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8, description="La contraseña debe tener al menos 8 caracteres")

# 3. Salida: Lo que va al frontend 
class UsuarioResponse(UsuarioBase):
    id: UUID
    rol: str
    fecha_registro: datetime

    class Config:
        from_attributes = True # Esto ayuda a que Pydantic lea los datos de la base de datos fácilmente

# 4.Iniciar Sesión
class UsuarioLogin(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico registrado")
    password: str = Field(..., description="Contraseña en texto plano")        