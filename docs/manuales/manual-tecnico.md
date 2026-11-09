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
| `SUPABASE_URL` | URL del proyecto, sin barra final: `https://<id>.supabase.co` | El id es el que aparece en la dirección del panel: `supabase.com/dashboard/project/<id>` |
| `SUPABASE_SERVICE_KEY` | Clave secreta de Supabase (`sb_secret_...`). Solo va en el backend, nunca en el frontend | Supabase → Project Settings (engranaje) → API Keys → Secret keys |
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

## Fotos de las publicaciones

En Supabase → Storage, crear un bucket llamado `publicaciones`: público, con límite de 5 MB por archivo y tipos permitidos `image/jpeg`, `image/png` e `image/webp`.

Para subir una foto, el frontend pide `POST /api/publicaciones/fotos` con `{"tipo_archivo": "image/jpeg"}`, hace `PUT` del archivo a `url_subida` con ese mismo `Content-Type`, y manda `url_publica` en `imagenes_urls` al crear la publicación.

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

## Frontend

```powershell
cd frontend
npm install
$env:VITE_API_URL = "http://localhost:8000"
npm run dev
```

Prueba de navegador del recorrido completo: necesita Chrome, la base de prueba de la sección Tests, el backend en el puerto 8001 apuntando a esa base (`DATABASE_URL`, con valores falsos en `MP_ACCESS_TOKEN` y `SUPABASE_URL`) y el frontend en el 5173 con `VITE_API_URL` en `http://localhost:8001`. Se corre con `..\backend\venv\Scripts\python.exe e2e\reset.py` y `node e2e\flujo.mjs` desde `frontend`, y deja capturas en `e2e/capturas`.

### Despliegue en Vercel

1. Si la base ya existía, ejecutar una sola vez `backend/database/migraciones/2026-11-colegios-a-pedido.sql` en el SQL Editor de Supabase.
2. En Vercel: Add New → Project → el mismo repositorio, con **Root Directory** `frontend`. Vercel detecta Vite.
3. Cargar `VITE_API_URL` con la URL del backend, sin barra final, y desplegar.
4. En el proyecto del backend, cargar `FRONTEND_URL` con la URL del frontend, sin barra final, y volver a desplegar. Habilita CORS y la vuelta desde Mercado Pago.

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
