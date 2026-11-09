from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional

class InstitucionBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=150, description="Nombre oficial del colegio")
    ciudad: str = Field(..., min_length=3, max_length=100, description="Ciudad donde se encuentra")
    provincia: str = Field(default="Buenos Aires", max_length=100, description="Provincia de la institución")

class InstitucionCreate(InstitucionBase):
    pass

class SolicitudResolucion(BaseModel):
    resultado: Literal['aceptada', 'duplicada', 'rechazada']
    institucion_id: Optional[int] = Field(None, description="Colegio ya existente, cuando la solicitud está duplicada")

class InstitucionResponse(InstitucionBase):
    id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True