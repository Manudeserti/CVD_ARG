from fastapi import FastAPI
from routers import institucion_router

# Inicializamos la API
app = FastAPI(
    title="API - Plataforma Escolar",
    description="Backend transaccional para compra/venta de uniformes",
    version="1.0.0"
)

# Conectamos los routers modulares a la aplicación principal
app.include_router(institucion_router.router)

# Endpoint 1: Health Check
@app.get("/", tags=["Estado"])
def read_root():
    return {"status": "ok", "message": "Servidor FastAPI funcionando con arquitectura modular."}