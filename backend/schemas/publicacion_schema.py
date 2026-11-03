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

class PublicacionCreate(PublicacionBase):
    pass 

class PublicacionResponse(PublicacionBase):
    id: UUID
    vendedor_id: UUID
    estado: Literal['disponible', 'reservado', 'vendido', 'baja']
    fecha_publicacion: datetime

    class Config:
        from_attributes = True