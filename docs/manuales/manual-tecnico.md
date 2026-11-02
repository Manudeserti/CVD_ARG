# Manual técnico: instalación y despliegue

> Borrador (Sprint B). Se completa con capturas cuando el despliegue esté hecho.

## Requisitos

- Python 3.12 o superior
- Docker (solo para correr los tests)
- Cuentas gratuitas en Supabase, Vercel, GitHub y Mercado Pago Developers

## Variables de entorno del backend

| Variable | Qué es | Dónde se obtiene |
|---|---|---|
| `DATABASE_URL` | Conexión a PostgreSQL | Supabase → Connect → Transaction pooler (puerto 6543) |
| `SECRET_KEY` | Firma de los tokens JWT (32 bytes o más) | `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `MP_ACCESS_TOKEN` | Credencial privada de Mercado Pago | Mercado Pago Developers → Tus integraciones → la aplicación → Credenciales de prueba |
| `MP_WEBHOOK_SECRET` | Clave para verificar la firma de los webhooks | Mercado Pago Developers → la aplicación → Webhooks → Configurar notificaciones |
| `BACKEND_URL` | URL pública del backend, sin barra final | Vercel, después del primer despliegue |
| `FRONTEND_URL` | URL pública del frontend (opcional hasta que exista) | Vercel |
| `CRON_SECRET` | Autoriza la tarea programada diaria | Se genera igual que `SECRET_KEY` |

## Base de datos

1. Crear un proyecto en Supabase (región East US).
2. En el SQL Editor, ejecutar `backend/database/schema.sql`.
3. Registrar un usuario desde la API y darle rol de administrador:
   ```sql
   UPDATE usuarios SET rol = 'admin' WHERE email = '...';
   ```

## Ejecución local

```powershell
cd backend
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe -m uvicorn main:app --reload
```

Documentación interactiva de la API: http://localhost:8000/docs

## Tests

```powershell
docker run -d --name cvd-test-db -e POSTGRES_PASSWORD=test -e POSTGRES_DB=cvd_test -p 5433:5432 postgres:16-alpine
venv\Scripts\python.exe -m pip install -r requirements-dev.txt
$env:TEST_DATABASE_URL = "postgresql://postgres:test@localhost:5433/cvd_test"
venv\Scripts\python.exe -m pytest
```

Los tests borran y recrean la base indicada en `TEST_DATABASE_URL`: nunca apuntarla a Supabase. Mercado Pago se simula, así que no hacen llamadas externas.

## Despliegue del backend en Vercel

1. En Vercel: Add New → Project → importar el repositorio de GitHub.
2. **Root Directory:** `backend`. Vercel detecta FastAPI por `main.py`.
3. Cargar las variables de entorno de la tabla anterior (Settings → Environment Variables).
4. Deploy. Copiar la URL asignada y cargarla como `BACKEND_URL`; volver a desplegar.
5. La tarea programada diaria se crea sola a partir de `backend/vercel.json`.

## Mercado Pago (sandbox)

1. Crear una aplicación en Mercado Pago Developers (producto: Checkout Pro).
2. Crear dos cuentas de prueba: una vendedora (sus credenciales de prueba van en `MP_ACCESS_TOKEN`) y una compradora (para pagar).
3. En Webhooks, configurar la URL `{BACKEND_URL}/api/pagos/webhook` con el evento **Pagos**, y copiar la clave secreta en `MP_WEBHOOK_SECRET`.
