# Manual técnico: instalación y despliegue

> Borrador (Sprint B). Backend desplegado en https://cvd-arg.vercel.app; faltan capturas.

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

1. Crear una aplicación en Mercado Pago Developers (producto: Checkout Pro). Mercado Pago crea sola la cuenta vendedora de prueba; las **credenciales de prueba** de la aplicación (empiezan con `APP_USR-`) van en `MP_ACCESS_TOKEN`.
2. En **Cuentas de prueba**, crear solo una cuenta **compradora**.
3. En Webhooks, configurar la URL `{BACKEND_URL}/api/pagos/webhook` con el evento **Pagos** (la misma URL para modo de prueba y productivo), y copiar la clave secreta en `MP_WEBHOOK_SECRET`. Volver a desplegar en Vercel.

### Compra de prueba

1. Con la API, registrar un vendedor y un comprador, publicar un artículo, reservarlo y pedir `POST /api/transacciones/{id}/pago`.
2. Abrir el `url_pago` en una **ventana de incógnito** e iniciar sesión con la cuenta compradora de prueba.
3. Pagar con la tarjeta de prueba Mastercard `5031 7557 3453 0604`, vencimiento `11/30`, CVV `123`, titular `APRO` (aprueba el pago), DNI `12345678`.
4. La operación pasa a `retenido` cuando llega el webhook.

Limitación: el entorno de pruebas rechaza las devoluciones (`401 · Unauthorized use of live credentials`), así que cancelar una operación pagada da 502 y la deja como estaba. Detalle en el capítulo 04 de la memoria.
