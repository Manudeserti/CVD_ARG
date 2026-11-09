import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import institucion_router
from routers import usuario_router
from routers import publicacion_router
from routers import transaccion_router
from routers import pago_router

# Inicializamos la API
app = FastAPI(
    title="API - Plataforma Escolar",
    description="Backend transaccional para compra/venta de uniformes",
    version="1.0.0"
)

# El frontend vive en otro dominio. La sesión viaja en el header Authorization, así que no hacen falta cookies.
origenes = ["http://localhost:5173"]
if os.getenv("FRONTEND_URL"):
    origenes.append(os.environ["FRONTEND_URL"])
app.add_middleware(CORSMiddleware, allow_origins=origenes, allow_methods=["*"], allow_headers=["Authorization", "Content-Type"])

# Conectamos los routers modulares a la aplicación principal
app.include_router(institucion_router.router)
app.include_router(usuario_router.router)
app.include_router(publicacion_router.router)
app.include_router(transaccion_router.router)
app.include_router(pago_router.router)
# Endpoint 1: Health Check
@app.get("/", tags=["Estado"])
def read_root():
    return {"status": "ok", "message": "Servidor FastAPI funcionando con arquitectura modular."}