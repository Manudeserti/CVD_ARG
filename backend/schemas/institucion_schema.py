from pydantic import BaseModel, Field

class InstitucionCreate(BaseModel):
    # Definimos las reglas estrictas de lo que aceptamos
    nombre: str = Field(..., min_length=3, max_length=150, description="Nombre oficial del colegio")
    ciudad: str = Field(..., min_length=3, max_length=100, description="Ciudad donde se ubica")