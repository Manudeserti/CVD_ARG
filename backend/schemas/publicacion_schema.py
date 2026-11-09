from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class PublicacionBase(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=2000)

    # NUEVO: Lista de categorías actualizada
    categoria: Literal['indumentaria', 'utiles', 'libros', 'instrumentos', 'deportes'] = Field(
        ...,
        description="Categoría principal del artículo"
    )

    talle: Optional[Literal[
        '4', '6', '8', '10', '12', '14', '16',
        'XS', 'S', 'M', 'L', 'XL', 'XXL', 'Unico'
    ]] = Field(None, description="Talle (solo aplica para indumentaria)")

    tipo: Literal['venta', 'donacion'] = Field(...)
    # Mismo rango que la columna NUMERIC(10, 2); sin negativos (una donación con precio -5 pasaba)
    precio: Decimal = Field(default=0.00, ge=0, max_digits=10, decimal_places=2)
    institucion_id: Optional[int] = None
    imagenes_urls: List[str] = Field(default=[])

class ColegioNuevo(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=150)
    ciudad: str = Field(..., min_length=3, max_length=100)
    provincia: str = Field(..., min_length=3, max_length=100)

class PublicacionCreate(PublicacionBase):
    imagenes_urls: List[str] = Field(default=[], max_length=5)
    # Si el colegio no está en la lista, se pide el alta y la publicación espera a que se resuelva
    colegio_nuevo: Optional[ColegioNuevo] = None

class FotoSubida(BaseModel):
    tipo_archivo: Literal['image/jpeg', 'image/png', 'image/webp']

class CambioDeColegio(BaseModel):
    institucion_id: int

class PublicacionResponse(PublicacionBase):
    id: UUID
    vendedor_id: UUID
    estado: Literal['disponible', 'reservado', 'vendido', 'baja', 'pendiente_colegio', 'borrador']
    fecha_publicacion: datetime

    class Config:
        from_attributes = True

class PublicacionPropia(PublicacionResponse):
    aviso: Optional[str] = None  # Solo lo ve el dueño: por eso no está en la respuesta pública
