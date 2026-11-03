from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime

# 1. Molde Base:  datos que comparten la creación y la respuesta
class UsuarioBase(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico válido")
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    telefono: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto opcional")

    # Juan@mail.com y juan@mail.com son la misma cuenta
    @field_validator("email")
    @classmethod
    def email_en_minusculas(cls, v: str) -> str:
        return v.lower()

# 2. Molde de Entrada: Lo que pone alguien que se registra
class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8, description="La contraseña debe tener al menos 8 caracteres")

    # bcrypt solo procesa hasta 72 bytes y con más falla: lo avisamos en lugar de responder 500
    @field_validator("password")
    @classmethod
    def password_hasta_72_bytes(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("La contraseña no puede superar los 72 bytes")
        return v

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

    @field_validator("email")
    @classmethod
    def email_en_minusculas(cls, v: str) -> str:
        return v.lower()        