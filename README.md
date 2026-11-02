# CVD_ARG
Web application for buying, selling, and donating school uniforms.

Trabajo Final de Ingeniería en Informática (UNMdP). Documentación del proyecto en [`docs/`](docs/README.md).

## Backend

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Crear `backend/.env` con:

```
DATABASE_URL=postgresql://...      # cadena de conexión de Supabase
SECRET_KEY=...                     # al menos 32 bytes: python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Correr con `uvicorn main:app --reload` y abrir http://localhost:8000/docs.

### Tests

Necesitan un Postgres descartable (borran todo):

```powershell
docker run -d --name cvd-test-db -e POSTGRES_PASSWORD=test -e POSTGRES_DB=cvd_test -p 5433:5432 postgres:16-alpine
pip install -r requirements-dev.txt
$env:TEST_DATABASE_URL = "postgresql://postgres:test@localhost:5433/cvd_test"
pytest
```
