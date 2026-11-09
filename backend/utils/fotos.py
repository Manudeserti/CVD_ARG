"""
Fotos de las publicaciones en Supabase Storage.
El navegador sube directo a Storage con una URL firmada: Vercel corta los pedidos de más de 4,5 MB
y una foto de celular puede superarlos. El tamaño y el tipo de archivo los hace cumplir el bucket.
"""
import os
import re
from uuid import uuid4

import httpx

BUCKET = "publicaciones"
EXTENSIONES = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


def _prefijo_publico(usuario_id) -> str:
    return f"{os.environ['SUPABASE_URL']}/storage/v1/object/public/{BUCKET}/{usuario_id}/"


def crear_url_subida(usuario_id, tipo_archivo: str) -> dict:
    """
    Pide a Storage una URL firmada para subir una foto nueva a la carpeta del usuario.
    La clave de servicio nunca sale del backend; al navegador solo le llega el token de esa foto.
    """
    nombre = f"{uuid4()}.{EXTENSIONES[tipo_archivo]}"
    url_firma = f"{os.environ['SUPABASE_URL']}/storage/v1/object/upload/sign/{BUCKET}/{usuario_id}/{nombre}"
    clave = os.environ["SUPABASE_SERVICE_KEY"]

    # ponytail: no hay tope de subidas por usuario ni limpieza de fotos huérfanas; sumarlos si el bucket se acerca al 1 GB gratuito
    respuesta = httpx.post(url_firma, headers={"apikey": clave, "Authorization": f"Bearer {clave}"}, timeout=15)
    if respuesta.is_error:
        raise RuntimeError(f"{respuesta.status_code} {respuesta.text}")

    return {
        "url_subida": f"{url_firma}?token={respuesta.json()['token']}",
        "url_publica": _prefijo_publico(usuario_id) + nombre
    }


def es_foto_del_usuario(url: str, usuario_id) -> bool:
    """Evita guardar enlaces externos o fotos de otro usuario. Exige el formato exacto que genera crear_url_subida."""
    extensiones = "|".join(EXTENSIONES.values())
    return re.fullmatch(re.escape(_prefijo_publico(usuario_id)) + rf"[0-9a-f-]{{36}}\.({extensiones})", url) is not None
