from fastapi import APIRouter, HTTPException, Request, status
from database.database import get_db_connection
from utils import pagos

router = APIRouter(
    prefix="/api/pagos",
    tags=["Pagos (Mercado Pago)"]
)


@router.post("/webhook", status_code=status.HTTP_200_OK)
def webhook_mercadopago(request: Request):
    """
    Recibe las notificaciones de Mercado Pago.
    Cuando un pago se aprueba, la transacción pasa de 'pendiente' a 'retenido'.
    Mercado Pago reintenta si no respondemos 200, así que tiene que poder recibir el mismo aviso varias veces.
    """
    data_id = request.query_params.get("data.id")

    # 1. Solo aceptamos avisos firmados por Mercado Pago
    if not pagos.firma_valida(request.headers.get("x-signature"), request.headers.get("x-request-id"), data_id):
        raise HTTPException(status_code=401, detail="Firma inválida")

    if request.query_params.get("type") != "payment" or not data_id:
        return {"status": "ignorado"}

    # 2. Consultamos el pago a Mercado Pago en lugar de creerle al cuerpo del aviso
    pago = pagos.obtener_pago(data_id)
    if pago.get("status") != "approved" or not pago.get("external_reference"):
        return {"status": "ignorado"}

    conexion = get_db_connection()
    cursor = conexion.cursor()

    try:
        cursor.execute('''
            SELECT estado_pago FROM transacciones_escrow WHERE id = %s FOR UPDATE;
        ''', (pago["external_reference"],))
        transaccion = cursor.fetchone()

        if not transaccion:
            return {"status": "ignorado"}

        estado_actual = transaccion[0]

        if estado_actual == 'pendiente':
            # 3. Caso normal: el dinero queda retenido hasta el escaneo del QR
            cursor.execute('''
                UPDATE transacciones_escrow SET estado_pago = 'retenido', id_pago_externo = %s WHERE id = %s;
            ''', (str(pago["id"]), pago["external_reference"]))

        elif estado_actual == 'cancelado':
            # 4. Pagó una operación que ya estaba cancelada (por ejemplo, venció la reserva): se devuelve
            pagos.reembolsar(str(pago["id"]), f"tardio-{pago['id']}")
            cursor.execute('''
                UPDATE transacciones_escrow SET estado_pago = 'reembolsado', id_pago_externo = %s WHERE id = %s;
            ''', (str(pago["id"]), pago["external_reference"]))

        # Cualquier otro estado significa que este aviso ya se procesó antes

        conexion.commit()
        return {"status": "ok"}

    except Exception as e:
        conexion.rollback()
        # Respondemos error para que Mercado Pago reintente más tarde
        raise HTTPException(status_code=500, detail=f"Error al procesar el pago: {str(e)}")
    finally:
        cursor.close()
        conexion.close()
