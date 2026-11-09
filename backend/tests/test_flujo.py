"""
Tests de punta a punta del flujo de compra, pago, donación, cancelación y vencimiento.
Mercado Pago se reemplaza por un doble en memoria: los tests no hacen llamadas reales.

Corren contra un Postgres de prueba (NUNCA contra Supabase: borran todo).
    docker run -d --name cvd-test-db -e POSTGRES_PASSWORD=test -e POSTGRES_DB=cvd_test -p 5433:5432 postgres:16-alpine
    $env:TEST_DATABASE_URL = "postgresql://postgres:test@localhost:5433/cvd_test"
    pip install -r requirements-dev.txt
    pytest
"""
import hashlib
import hmac
import os
import sys
from pathlib import Path
from uuid import uuid4

import httpx
import psycopg2
import pytest

TEST_DB = os.getenv("TEST_DATABASE_URL")
if not TEST_DB:
    pytest.skip("Definí TEST_DATABASE_URL para correr estos tests", allow_module_level=True)

# Tienen que estar definidas antes de importar la app (load_dotenv no pisa variables ya existentes)
os.environ["DATABASE_URL"] = TEST_DB
os.environ["SECRET_KEY"] = "clave-solo-para-tests-de-32-bytes-o-mas"
os.environ["MP_WEBHOOK_SECRET"] = "secreto-webhook-de-prueba"
os.environ["CRON_SECRET"] = "secreto-cron-de-prueba"
BACKEND = Path(__file__).parents[1]
sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient  # noqa: E402
from main import app  # noqa: E402
from utils import fotos, pagos  # noqa: E402

client = TestClient(app)
CRON = {"Authorization": f"Bearer {os.environ['CRON_SECRET']}"}


class MercadoPagoFalso:
    """Reemplaza las llamadas a la API de Mercado Pago y registra lo que se le pidió."""
    def __init__(self):
        self.pagos = {}        # pago_id -> respuesta de GET /v1/payments
        self.reembolsos = []   # pago_id de cada devolución

    def crear_preferencia(self, transaccion_id, titulo, monto):
        return f"https://mercadopago.test/checkout?ref={transaccion_id}"

    def obtener_pago(self, pago_id):
        return self.pagos[pago_id]

    def reembolsar(self, pago_id, clave_idempotencia):
        self.reembolsos.append(pago_id)


@pytest.fixture(autouse=True)
def mp(monkeypatch):
    falso = MercadoPagoFalso()
    for nombre in ("crear_preferencia", "obtener_pago", "reembolsar"):
        monkeypatch.setattr(pagos, nombre, getattr(falso, nombre))
    return falso


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


def avisar_pago(pago_id, secreto=None):
    """Envía el webhook tal como lo firma Mercado Pago."""
    ts, request_id = "1700000000", uuid4().hex
    manifest = f"id:{pago_id};request-id:{request_id};ts:{ts};"
    firma = hmac.new((secreto or os.environ["MP_WEBHOOK_SECRET"]).encode(), manifest.encode(), hashlib.sha256).hexdigest()
    return client.post(
        f"/api/pagos/webhook?data.id={pago_id}&type=payment",
        headers={"x-signature": f"ts={ts},v1={firma}", "x-request-id": request_id},
        json={"type": "payment", "data": {"id": pago_id}}
    )


def pagar(mp, transaccion_id):
    """El comprador paga en Mercado Pago y llega el webhook de pago aprobado."""
    pago_id = str(len(mp.pagos) + 1000)
    mp.pagos[pago_id] = {"id": int(pago_id), "status": "approved", "external_reference": transaccion_id}
    assert avisar_pago(pago_id).status_code == 200
    return pago_id


def estado_publicacion(publicacion_id):
    return sql("SELECT estado FROM publicaciones WHERE id = %s", (publicacion_id,))[0][0]


def test_venta_completa(mp):
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

    # Solo el comprador obtiene el link de pago
    assert client.post(f"/api/transacciones/{compra['id']}/pago", headers=vendedor).status_code == 403
    r = client.post(f"/api/transacciones/{compra['id']}/pago", headers=comprador)
    assert r.status_code == 200 and compra["id"] in r.json()["url_pago"]

    pago_id = pagar(mp, compra["id"])
    assert sql("SELECT estado_pago, id_pago_externo FROM transacciones_escrow WHERE id = %s", (compra["id"],))[0] == ("retenido", pago_id)

    # Una vez pagada, no se puede volver a pagar
    assert client.post(f"/api/transacciones/{compra['id']}/pago", headers=comprador).status_code == 400

    contacto = client.get(f"/api/transacciones/{compra['id']}/contacto", headers=comprador)
    assert contacto.status_code == 200 and contacto.json()["email"].endswith("@test.com")
    assert client.get(f"/api/transacciones/{compra['id']}/contacto", headers=otro).status_code == 403

    # Solo el vendedor escanea
    assert client.post("/api/transacciones/liberar", headers=comprador, json=liberar).status_code == 403
    assert client.post("/api/transacciones/liberar", headers=vendedor, json=liberar).status_code == 200
    assert estado_publicacion(pub) == "vendido"

    # Una vez escaneado, ya no se puede cancelar
    assert client.post(f"/api/transacciones/{compra['id']}/cancelar", headers=comprador).status_code == 400


def test_cancelacion_reembolsa_y_devuelve_el_articulo_al_catalogo(mp):
    _, vendedor = usuario()
    _, comprador = usuario()
    _, otro = usuario()
    pub = publicar(vendedor)
    compra = comprar(comprador, pub).json()
    pago_id = pagar(mp, compra["id"])

    assert client.post(f"/api/transacciones/{compra['id']}/cancelar", headers=otro).status_code == 403

    r = client.post(f"/api/transacciones/{compra['id']}/cancelar", headers=comprador)
    assert r.status_code == 200 and r.json()["estado_pago"] == "reembolsado"
    assert mp.reembolsos == [pago_id]
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


def test_webhook_rechaza_firmas_falsas_y_es_idempotente(mp, monkeypatch):
    _, vendedor = usuario()
    _, comprador = usuario()
    compra = comprar(comprador, publicar(vendedor)).json()
    mp.pagos["555"] = {"id": 555, "status": "approved", "external_reference": compra["id"]}

    assert avisar_pago("555", secreto="otro-secreto").status_code == 401

    # Si falta la clave en el servidor, se rechaza el aviso en lugar de fallar con 500
    secreto = os.environ["MP_WEBHOOK_SECRET"]
    monkeypatch.delenv("MP_WEBHOOK_SECRET")
    assert avisar_pago("555", secreto=secreto).status_code == 401
    monkeypatch.setenv("MP_WEBHOOK_SECRET", secreto)
    assert sql("SELECT estado_pago FROM transacciones_escrow WHERE id = %s", (compra["id"],))[0][0] == "pendiente"

    # Mercado Pago reintenta: el mismo aviso dos veces no cambia nada la segunda vez
    assert avisar_pago("555").status_code == 200
    assert avisar_pago("555").status_code == 200
    assert sql("SELECT estado_pago FROM transacciones_escrow WHERE id = %s", (compra["id"],))[0][0] == "retenido"


def test_pago_tardio_de_una_reserva_vencida_se_devuelve(mp):
    _, vendedor = usuario()
    _, comprador = usuario()
    compra = comprar(comprador, publicar(vendedor)).json()
    assert client.post(f"/api/transacciones/{compra['id']}/cancelar", headers=comprador).json()["estado_pago"] == "cancelado"

    pago_id = pagar(mp, compra["id"])
    assert mp.reembolsos == [pago_id]
    assert sql("SELECT estado_pago FROM transacciones_escrow WHERE id = %s", (compra["id"],))[0][0] == "reembolsado"


def test_vencimientos(mp):
    _, vendedor = usuario()
    _, comprador = usuario()

    # Venta pagada sin encuentro después de 8 días: se reembolsa
    pub_pagada = publicar(vendedor)
    pagada = comprar(comprador, pub_pagada).json()
    pago_id = pagar(mp, pagada["id"])
    sql("UPDATE transacciones_escrow SET fecha_creacion = now() - interval '8 days' WHERE id = %s", (pagada["id"],))

    # Venta reservada sin pagar después de 25 horas: se cancela
    pub_impaga = publicar(vendedor)
    impaga = comprar(comprador, pub_impaga).json()
    sql("UPDATE transacciones_escrow SET fecha_creacion = now() - interval '25 hours' WHERE id = %s", (impaga["id"],))

    # Donación de hace 25 horas: todavía está dentro del plazo de encuentro
    donacion = comprar(comprador, publicar(vendedor, tipo="donacion", precio=0)).json()
    sql("UPDATE transacciones_escrow SET fecha_creacion = now() - interval '25 hours' WHERE id = %s", (donacion["id"],))

    # Donación de hace 5 días: vencida (las donaciones tienen 4 días, no 7)
    donacion_vieja = comprar(comprador, publicar(vendedor, tipo="donacion", precio=0)).json()
    sql("UPDATE transacciones_escrow SET fecha_creacion = now() - interval '5 days' WHERE id = %s", (donacion_vieja["id"],))

    # Solo el cron de Vercel puede ejecutarlo
    assert client.get("/api/transacciones/vencer", headers=comprador).status_code == 403

    assert client.get("/api/transacciones/vencer", headers=CRON).status_code == 200
    estado = lambda t: sql("SELECT estado_pago FROM transacciones_escrow WHERE id = %s", (t["id"],))[0][0]  # noqa: E731
    assert estado(pagada) == "reembolsado" and pago_id in mp.reembolsos
    assert estado(impaga) == "cancelado"
    assert estado(donacion) == "pendiente"
    assert estado(donacion_vieja) == "cancelado"
    assert estado_publicacion(pub_pagada) == estado_publicacion(pub_impaga) == "disponible"


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


def test_tope_de_donaciones_pendientes():
    _, donante = usuario()
    _, receptor = usuario()

    pedidas = [comprar(receptor, publicar(donante, tipo="donacion", precio=0)).json() for _ in range(3)]
    cuarta = publicar(donante, tipo="donacion", precio=0)
    assert comprar(receptor, cuarta).status_code == 400

    # Al cancelar una se libera un lugar
    client.post(f"/api/transacciones/{pedidas[0]['id']}/cancelar", headers=receptor)
    assert comprar(receptor, cuarta).status_code == 201

    # Las ventas no tienen tope
    assert all(comprar(receptor, publicar(donante)).status_code == 201 for _ in range(4))


def test_login_se_bloquea_temporalmente():
    email = f"{uuid4().hex[:8]}@test.com"
    client.post("/api/usuarios/", json={"email": email, "nombre": "Test", "apellido": "Usuario", "password": "clave-segura-123"})
    login = lambda password, mail=email: client.post("/api/usuarios/login", json={"email": mail, "password": password})  # noqa: E731

    # El email no distingue mayúsculas
    assert login("clave-segura-123", email.upper()).status_code == 200

    assert all(login("incorrecta").status_code == 401 for _ in range(5))
    # Bloqueada: ni con la contraseña correcta
    assert login("clave-segura-123").status_code == 429

    # Pasado el bloqueo vuelve a funcionar
    sql("UPDATE usuarios SET bloqueado_hasta = now() - interval '1 minute' WHERE email = %s", (email,))
    assert login("clave-segura-123").status_code == 200


def test_validaciones_de_datos():
    _, admin = usuario(admin=True)
    _, vendedor = usuario()
    publicar_con = lambda **datos: client.post("/api/publicaciones/", headers=vendedor, json={  # noqa: E731
        "titulo": "Buzo del colegio", "categoria": "indumentaria", **datos})

    # Precios
    assert publicar_con(tipo="donacion", precio=-5).status_code == 422
    assert publicar_con(tipo="venta", precio=0).status_code == 400
    assert publicar_con(tipo="venta", precio=1_000_000_000).status_code == 422
    with pytest.raises(psycopg2.errors.CheckViolation):
        sql("UPDATE publicaciones SET precio = 0 WHERE tipo = 'venta'")

    # Contraseñas de más de 72 bytes: error claro en el registro, credenciales incorrectas en el login
    r = client.post("/api/usuarios/", json={"email": f"{uuid4().hex[:8]}@test.com", "nombre": "Test", "apellido": "Usuario", "password": "x" * 73})
    assert r.status_code == 422
    assert client.post("/api/usuarios/login", json={"email": "nadie@test.com", "password": "x" * 80}).status_code == 401

    # Errores del pedido, no del servidor
    assert publicar_con(tipo="venta", precio=100, institucion_id=999999).status_code == 400
    con_publicaciones = institucion()
    publicar(vendedor, institucion_id=con_publicaciones)
    assert client.delete(f"/api/instituciones/{con_publicaciones}", headers=admin).status_code == 409


def test_fotos_de_publicaciones(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://proyecto.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "clave-de-prueba")
    respuesta_storage = httpx.Response(200, json={"token": "token-firmado"})
    monkeypatch.setattr(fotos.httpx, "post", lambda url, **kwargs: respuesta_storage)

    _, vendedor = usuario()
    _, otro = usuario()
    pedir = lambda tipo, headers=vendedor: client.post(  # noqa: E731
        "/api/publicaciones/fotos", headers=headers, json={"tipo_archivo": tipo})
    publicar_con = lambda urls, headers=vendedor: client.post("/api/publicaciones/", headers=headers, json={  # noqa: E731
        "titulo": "Buzo con foto", "categoria": "indumentaria", "tipo": "donacion", "imagenes_urls": urls})

    assert pedir("image/jpeg", headers={}).status_code == 401
    assert pedir("application/pdf").status_code == 422

    r = pedir("image/jpeg")
    assert r.status_code == 200, r.text
    assert r.json()["url_subida"].endswith("?token=token-firmado")
    url = r.json()["url_publica"]

    creada = publicar_con([url])
    assert creada.status_code == 201, creada.text
    assert creada.json()["imagenes_urls"] == [url]

    # Solo fotos propias, con el formato exacto, y hasta 5
    carpeta = url.rsplit("/", 1)[0]
    assert publicar_con([url], headers=otro).status_code == 400
    assert publicar_con(["https://otro-sitio.test/foto.jpg"]).status_code == 400
    assert publicar_con([f"{carpeta}/../{uuid4()}.jpg"]).status_code == 400
    assert publicar_con([f"{carpeta}/{uuid4()}.svg"]).status_code == 400
    assert publicar_con([url] * 6).status_code == 422

    respuesta_storage.status_code = 500
    assert pedir("image/png").status_code == 502


def test_catalogo_paginado():
    _, vendedor = usuario()
    colegio = institucion(provincia="Tierra del Fuego", ciudad="Ushuaia")
    publicadas = {publicar(vendedor, institucion_id=colegio) for _ in range(3)}

    pagina = lambda offset: [p["id"] for p in client.get(  # noqa: E731
        f"/api/publicaciones/?institucion_id={colegio}&limit=2&offset={offset}").json()]
    primera, segunda = pagina(0), pagina(2)
    assert len(primera) == 2 and len(segunda) == 1
    assert set(primera) | set(segunda) == publicadas
