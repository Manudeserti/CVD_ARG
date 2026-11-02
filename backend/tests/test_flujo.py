"""
Tests de punta a punta del flujo de compra, donación, cancelación y vencimiento.

Corren contra un Postgres de prueba (NUNCA contra Supabase: borran todo).
    docker run -d --name cvd-test-db -e POSTGRES_PASSWORD=test -e POSTGRES_DB=cvd_test -p 5433:5432 postgres:16-alpine
    $env:TEST_DATABASE_URL = "postgresql://postgres:test@localhost:5433/cvd_test"
    pip install -r requirements-dev.txt
    pytest
"""
import os
import sys
from pathlib import Path
from uuid import uuid4

import psycopg2
import pytest

TEST_DB = os.getenv("TEST_DATABASE_URL")
if not TEST_DB:
    pytest.skip("Definí TEST_DATABASE_URL para correr estos tests", allow_module_level=True)

# Tienen que estar definidas antes de importar la app (load_dotenv no pisa variables ya existentes)
os.environ["DATABASE_URL"] = TEST_DB
os.environ["SECRET_KEY"] = "clave-solo-para-tests-de-32-bytes-o-mas"
BACKEND = Path(__file__).parents[1]
sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient  # noqa: E402
from main import app  # noqa: E402

client = TestClient(app)


def sql(query, params=()):
    conexion = psycopg2.connect(TEST_DB)
    with conexion, conexion.cursor() as cursor:
        cursor.execute(query, params)
        resultado = cursor.fetchall() if cursor.description else None
    conexion.close()
    return resultado


@pytest.fixture(scope="module", autouse=True)
def base_limpia():
    sql("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
    sql((BACKEND / "database" / "schema.sql").read_text(encoding="utf-8"))


def usuario(admin=False):
    """Registra un usuario nuevo y devuelve (id, headers con su token)."""
    email = f"{uuid4().hex[:8]}@test.com"
    r = client.post("/api/usuarios/", json={
        "email": email, "nombre": "Test", "apellido": "Usuario", "password": "clave-segura-123"
    })
    assert r.status_code == 201, r.text
    if admin:
        sql("UPDATE usuarios SET rol = 'admin' WHERE email = %s", (email,))
    r = client.post("/api/usuarios/login", json={"email": email, "password": "clave-segura-123"})
    return r.json()["usuario"]["id"], {"Authorization": f"Bearer {r.json()['access_token']}"}


def institucion(provincia="Buenos Aires", ciudad="Mar del Plata"):
    return sql(
        "INSERT INTO instituciones (nombre, ciudad, provincia) VALUES ('Colegio Test', %s, %s) RETURNING id",
        (ciudad, provincia)
    )[0][0]


def publicar(headers, tipo="venta", precio=10000, institucion_id=None):
    r = client.post("/api/publicaciones/", headers=headers, json={
        "titulo": "Buzo del colegio", "categoria": "indumentaria", "talle": "10",
        "tipo": tipo, "precio": precio, "institucion_id": institucion_id
    })
    assert r.status_code == 201, r.text
    return r.json()["id"]


def comprar(headers, publicacion_id):
    return client.post("/api/transacciones/", headers=headers, json={"publicacion_id": publicacion_id})


def simular_pago_aprobado(transaccion_id):
    # Lo que en el Sprint B va a hacer el webhook de Mercado Pago
    sql("UPDATE transacciones_escrow SET estado_pago = 'retenido' WHERE id = %s", (transaccion_id,))


def estado_publicacion(publicacion_id):
    return sql("SELECT estado FROM publicaciones WHERE id = %s", (publicacion_id,))[0][0]


def test_venta_completa():
    _, vendedor = usuario()
    _, comprador = usuario()
    _, otro = usuario()
    pub = publicar(vendedor)

    r = comprar(comprador, pub)
    assert r.status_code == 201
    compra = r.json()
    assert compra["comision_plataforma"] == "500.00"
    assert compra["qr_token"]

    # Nadie más puede comprar un artículo reservado
    assert comprar(otro, pub).status_code == 400

    # El vendedor nunca ve el QR del comprador
    historial = client.get("/api/transacciones/mis-transacciones", headers=vendedor).json()
    assert historial[0]["qr_token"] is None

    # Sin pago confirmado: ni escaneo ni datos de contacto
    liberar = {"qr_token": compra["qr_token"]}
    assert client.post("/api/transacciones/liberar", headers=vendedor, json=liberar).status_code == 400
    assert client.get(f"/api/transacciones/{compra['id']}/contacto", headers=comprador).status_code == 400

    simular_pago_aprobado(compra["id"])

    contacto = client.get(f"/api/transacciones/{compra['id']}/contacto", headers=comprador)
    assert contacto.status_code == 200 and contacto.json()["email"].endswith("@test.com")
    assert client.get(f"/api/transacciones/{compra['id']}/contacto", headers=otro).status_code == 403

    # Solo el vendedor escanea
    assert client.post("/api/transacciones/liberar", headers=comprador, json=liberar).status_code == 403
    assert client.post("/api/transacciones/liberar", headers=vendedor, json=liberar).status_code == 200
    assert estado_publicacion(pub) == "vendido"

    # Una vez escaneado, ya no se puede cancelar
    assert client.post(f"/api/transacciones/{compra['id']}/cancelar", headers=comprador).status_code == 400


def test_cancelacion_devuelve_el_articulo_al_catalogo():
    _, vendedor = usuario()
    _, comprador = usuario()
    _, otro = usuario()
    pub = publicar(vendedor)
    compra = comprar(comprador, pub).json()
    simular_pago_aprobado(compra["id"])

    assert client.post(f"/api/transacciones/{compra['id']}/cancelar", headers=otro).status_code == 403

    r = client.post(f"/api/transacciones/{compra['id']}/cancelar", headers=comprador)
    assert r.status_code == 200 and r.json()["estado_pago"] == "reembolsado"
    assert estado_publicacion(pub) == "disponible"

    # El QR de una operación cancelada ya no sirve
    r = client.post("/api/transacciones/liberar", headers=vendedor, json={"qr_token": compra["qr_token"]})
    assert r.status_code == 400


def test_donacion_sin_pago():
    _, donante = usuario()
    _, receptor = usuario()
    pub = publicar(donante, tipo="donacion", precio=0)

    compra = comprar(receptor, pub).json()
    assert compra["comision_plataforma"] == "0.00"
    assert client.get(f"/api/transacciones/{compra['id']}/contacto", headers=receptor).status_code == 200

    r = client.post("/api/transacciones/liberar", headers=donante, json={"qr_token": compra["qr_token"]})
    assert r.status_code == 200
    assert estado_publicacion(pub) == "vendido"


def test_vencimiento_del_plazo_de_encuentro():
    _, admin = usuario(admin=True)
    _, vendedor = usuario()
    _, comprador = usuario()
    pub = publicar(vendedor)
    compra = comprar(comprador, pub).json()
    simular_pago_aprobado(compra["id"])
    sql("UPDATE transacciones_escrow SET fecha_creacion = now() - interval '8 days' WHERE id = %s", (compra["id"],))

    assert client.post("/api/transacciones/vencer", headers=comprador).status_code == 403

    r = client.post("/api/transacciones/vencer", headers=admin)
    assert r.status_code == 200 and r.json()["vencidas"] >= 1
    assert sql("SELECT estado_pago FROM transacciones_escrow WHERE id = %s", (compra["id"],))[0][0] == "reembolsado"
    assert estado_publicacion(pub) == "disponible"


def test_catalogo_filtros_y_baja():
    _, admin = usuario(admin=True)
    _, vendedor = usuario()
    _, comprador = usuario()

    # Solo un admin gestiona instituciones
    nueva = {"nombre": "Escuela N° 1", "ciudad": "Rosario", "provincia": "Santa Fe"}
    assert client.post("/api/instituciones/", headers=vendedor, json=nueva).status_code == 403
    assert client.post("/api/instituciones/", headers=admin, json=nueva).status_code == 201
    assert all(i["provincia"] == "Santa Fe" for i in client.get("/api/instituciones/?provincia=santa fe").json())

    cordoba = institucion(provincia="Córdoba", ciudad="Villa María")
    pub = publicar(vendedor, institucion_id=cordoba)
    otra = publicar(vendedor, institucion_id=institucion(provincia="Mendoza", ciudad="Mendoza"))

    ids = [p["id"] for p in client.get("/api/publicaciones/?provincia=Córdoba").json()]
    assert pub in ids and otra not in ids

    # Una publicación reservada no aparece en el catálogo ni se puede dar de baja
    comprar(comprador, otra)
    assert otra not in [p["id"] for p in client.get("/api/publicaciones/").json()]
    assert client.delete(f"/api/publicaciones/{otra}", headers=vendedor).status_code == 400

    # Solo el dueño da de baja; después desaparece del catálogo y de "mis publicaciones"
    assert client.delete(f"/api/publicaciones/{pub}", headers=comprador).status_code == 403
    assert client.delete(f"/api/publicaciones/{pub}", headers=vendedor).status_code == 200
    assert pub not in [p["id"] for p in client.get("/api/publicaciones/").json()]
    assert pub not in [p["id"] for p in client.get("/api/publicaciones/mias", headers=vendedor).json()]
