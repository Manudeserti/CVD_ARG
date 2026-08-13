from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class PublicacionBase(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=100)
    descripcion: Optional[str] = None
    
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
    precio: Decimal = Field(default=0.00, decimal_places=2)
    institucion_id: Optional[int] = None
    imagenes_urls: List[str] = Field(default=[])

class PublicacionCreate(PublicacionBase):
    pass 

class PublicacionResponse(PublicacionBase):
    id: UUID
    vendedor_id: UUID
    estado: Literal['disponible', 'reservado', 'vendido']
    fecha_publicacion: datetime

    class Config:
        from_attributes = True