"""
Integración con la API de Mercado Pago (Checkout Pro).
Se usa httpx en lugar del SDK oficial: son cuatro operaciones REST y así no sumamos otra dependencia.
"""
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import httpx

API_MP = "https://api.mercadopago.com"
PLAZO_PAGO_HORAS = 24 # Después de esto la preferencia vence y la reserva sin pagar se libera


def _headers(extra: dict = None) -> dict:
    return {"Authorization": f"Bearer {os.environ['MP_ACCESS_TOKEN']}", **(extra or {})}


def _verificar(respuesta: httpx.Response) -> None:
    """Como raise_for_status, pero con el mensaje de Mercado Pago, que explica el motivo del rechazo."""
    if respuesta.is_error:
        raise RuntimeError(f"{respuesta.status_code} {respuesta.text}")


def crear_preferencia(transaccion_id: str, titulo: str, monto) -> str:
    """
    Crea la preferencia de pago y devuelve la URL de Checkout Pro a la que se redirige al comprador.
    El id de la transacción viaja como external_reference para reconocerla cuando llegue el webhook.
    """
    vence = datetime.now(timezone.utc) + timedelta(hours=PLAZO_PAGO_HORAS)
    preferencia = {
        "items": [{
            "id": transaccion_id,
            "title": titulo,
            "quantity": 1,
            "currency_id": "ARS",
            "unit_price": float(monto)
        }],
        "external_reference": transaccion_id,
        "notification_url": f"{os.environ['BACKEND_URL']}/api/pagos/webhook",
        "expires": True,
        "expiration_date_to": vence.isoformat(timespec="milliseconds")
    }

    # Mientras no exista el frontend publicado no hay a dónde volver después de pagar
    frontend = os.getenv("FRONTEND_URL")
    if frontend:
        url_vuelta = f"{frontend}/transacciones/{transaccion_id}"
        preferencia["back_urls"] = {"success": url_vuelta, "failure": url_vuelta, "pending": url_vuelta}
        preferencia["auto_return"] = "approved"

    respuesta = httpx.post(f"{API_MP}/checkout/preferences", headers=_headers(), json=preferencia, timeout=15)
    _verificar(respuesta)
    return respuesta.json()["init_point"]


def obtener_pago(pago_id: str) -> dict:
    """Consulta un pago directamente a Mercado Pago. Nunca confiamos en el cuerpo del webhook."""
    respuesta = httpx.get(f"{API_MP}/v1/payments/{pago_id}", headers=_headers(), timeout=15)
    _verificar(respuesta)
    return respuesta.json()


def reembolsar(pago_id: str, clave_idempotencia: str) -> None:
    """
    Devuelve el total del pago al comprador.
    La clave de idempotencia hace que reintentar la misma devolución no la duplique.
    """
    respuesta = httpx.post(
        f"{API_MP}/v1/payments/{pago_id}/refunds",
        headers=_headers({"X-Idempotency-Key": clave_idempotencia}),
        json={},
        timeout=15
    )
    _verificar(respuesta)


def firma_valida(x_signature: str, x_request_id: str, data_id: str) -> bool:
    """
    Verifica que el webhook lo mandó Mercado Pago (HMAC-SHA256 con la clave secreta de la aplicación).
    Formato del header: "ts=1700000000,v1=<hash hex>".
    """
    partes = dict(p.strip().split("=", 1) for p in (x_signature or "").split(",") if "=" in p)
    manifest = f"id:{data_id};request-id:{x_request_id};ts:{partes.get('ts')};"
    secreto = os.getenv("MP_WEBHOOK_SECRET")
    if not secreto:
        return False  # Sin clave configurada no hay forma de validar: se rechaza el aviso
    esperado = hmac.new(secreto.encode(), manifest.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(esperado, partes.get("v1", ""))
