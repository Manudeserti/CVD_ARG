from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Literal

# 1. Lo único que recibimos del Frontend (Cero confianza)
class TransaccionCreate(BaseModel):
    publicacion_id: UUID = Field(..., description="ID del artículo que se quiere comprar")

# 2. Lo que le devolvemos al Frontend (El recibo completo de la bóveda)
class TransaccionResponse(BaseModel):
    id: UUID
    publicacion_id: UUID
    comprador_id: UUID
    vendedor_id: UUID
    
    # Datos financieros
    monto: Decimal = Field(..., decimal_places=2)
    comision_plataforma: Decimal = Field(..., decimal_places=2)
    id_pago_externo: Optional[str] = None
    estado_pago: Literal['pendiente', 'retenido', 'liberado', 'cancelado', 'reembolsado']
    
    # Seguridad y tiempos (el qr_token solo se le envía al comprador)
    qr_token: Optional[UUID] = None
    fecha_creacion: datetime
    fecha_liberacion: Optional[datetime] = None

    # Datos del artículo para mostrar el historial sin pedir cada publicación por separado
    titulo: Optional[str] = None
    tipo: Optional[Literal['venta', 'donacion']] = None
    imagen: Optional[str] = None

    class Config:
        from_attributes = True


# Este es el molde para cuando el vendedor escanea el QR
class TransaccionLiberar(BaseModel):
    qr_token: UUID = Field(..., description="El token único del código QR")



class ContactoResponse(BaseModel):
    nombre: str
    apellido: str
    email: str
    telefono: Optional[str] = None # Es opcional en el registro