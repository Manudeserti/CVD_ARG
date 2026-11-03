from fastapi import APIRouter, Depends, HTTPException, status
from decimal import Decimal
from uuid import UUID
from schemas.transaccion_schema import TransaccionCreate, TransaccionResponse, TransaccionLiberar, ContactoResponse
from database.database import get_db_connection, error_interno
from utils.security import get_usuario_actual, requerir_cron
from utils import pagos


router = APIRouter(
    prefix="/api/transacciones",
    tags=["Transacciones (Escrow)"]
)

PORCENTAJE_COMISION = Decimal('0.05') # 5% de comisión para la plataforma
# Si pasan estos días sin escanear el QR, la operación se cancela (y se reembolsa si había pago).
# Las donaciones tienen menos plazo: nadie puso dinero y el artículo queda bloqueado para el resto.
PLAZO_ENCUENTRO_DIAS = {'venta': 7, 'donacion': 4}
MAX_DONACIONES_PENDIENTES = 3 # Evita que una sola persona reserve todas las donaciones del catálogo

# Estado en el que tiene que estar la transacción para poder escanear el QR.
# Las ventas necesitan el pago confirmado (retenido); las donaciones no tienen pago.
ESTADO_PARA_LIBERAR = {'venta': 'retenido', 'donacion': 'pendiente'}

# Estados en los que cada parte puede ver los datos de contacto de la otra
ESTADOS_CON_CONTACTO = {'venta': ('retenido', 'liberado'), 'donacion': ('pendiente', 'liberado')}


@router.post("/", response_model=TransaccionResponse, status_code=status.HTTP_201_CREATED)
def iniciar_transaccion(
    compra: TransaccionCreate,
    usuario_actual = Depends(get_usuario_actual) # ¡La barrera VIP!
):
    """
    Inicia el proceso de compra (Escrow).
    Valida el stock, congela el precio, calcula la comisión y reserva el artículo.
    """
    comprador_id = usuario_actual["id"]

    conexion = get_db_connection()
    cursor = conexion.cursor()

    try:
        # 1. Buscamos el artículo y lo bloqueamos (FOR UPDATE) hasta el commit.
        # Si dos compradores llegan a la vez, el segundo espera y después ve el estado 'reservado'.
        cursor.execute('''
            SELECT vendedor_id, precio, estado, tipo
            FROM publicaciones
            WHERE id = %s
            FOR UPDATE;
        ''', (str(compra.publicacion_id),))

        publicacion = cursor.fetchone()

        if not publicacion:
            raise HTTPException(status_code=404, detail="El artículo no existe")

        vendedor_id, precio_original, estado_actual , tipo_publicacion = publicacion

        # 2. Validaciones estrictas de negocio
        if estado_actual != 'disponible':
            raise HTTPException(status_code=400, detail="El artículo ya no está disponible")

        if str(vendedor_id) == str(comprador_id):
            raise HTTPException(status_code=400, detail="No puedes comprar tu propio artículo")

        if tipo_publicacion == 'donacion':
            # Bloqueamos al usuario para que dos pedidos simultáneos no pasen ambos el tope
            cursor.execute("SELECT 1 FROM usuarios WHERE id = %s FOR UPDATE;", (str(comprador_id),))
            cursor.execute('''
                SELECT count(*)
                FROM transacciones_escrow t
                JOIN publicaciones p ON p.id = t.publicacion_id
                WHERE t.comprador_id = %s AND p.tipo = 'donacion' AND t.estado_pago = 'pendiente';
            ''', (str(comprador_id),))
            if cursor.fetchone()[0] >= MAX_DONACIONES_PENDIENTES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Ya tenés {MAX_DONACIONES_PENDIENTES} donaciones pendientes de retirar. Concretá o cancelá alguna antes de pedir otra."
                )

        # 3. Cálculos financieros
        if tipo_publicacion== 'venta':
            comision_calculada = precio_original * PORCENTAJE_COMISION
        else:
            #Si es donacion, no hay comision
            comision_calculada= Decimal('0.00')

        # === INICIO DE TRANSACCIÓN SQL ===

        # 4. Insertamos el recibo en la bóveda
        cursor.execute('''
            INSERT INTO transacciones_escrow
            (publicacion_id, comprador_id, vendedor_id, monto, comision_plataforma, estado_pago)
            VALUES (%s, %s, %s, %s, %s, 'pendiente')
            RETURNING id, publicacion_id, comprador_id, vendedor_id, monto, comision_plataforma,
                      id_pago_externo, estado_pago, qr_token, fecha_creacion, fecha_liberacion;
        ''', (
            str(compra.publicacion_id),
            str(comprador_id),
            str(vendedor_id),
            precio_original,
            comision_calculada
        ))

        nueva_transaccion = cursor.fetchone()

        # 5. Reservamos el artículo para que nadie más lo compre
        cursor.execute('''
            UPDATE publicaciones
            SET estado = 'reservado'
            WHERE id = %s;
        ''', (str(compra.publicacion_id),))

        # 6. Confirmamos los cambios (El momento en que todo se guarda definitivamente)
        conexion.commit()

        # 7. Armamos la respuesta mapeando lo que devolvió el RETURNING.
        # Quien llama acá es el comprador, así que sí puede recibir su qr_token.
        return {
            "id": nueva_transaccion[0],
            "publicacion_id": nueva_transaccion[1],
            "comprador_id": nueva_transaccion[2],
            "vendedor_id": nueva_transaccion[3],
            "monto": nueva_transaccion[4],
            "comision_plataforma": nueva_transaccion[5],
            "id_pago_externo": nueva_transaccion[6],
            "estado_pago": nueva_transaccion[7],
            "qr_token": nueva_transaccion[8],
            "fecha_creacion": nueva_transaccion[9],
            "fecha_liberacion": nueva_transaccion[10]
        }

    except HTTPException:
        conexion.rollback()
        raise
    except Exception as e:
        conexion.rollback()
        raise error_interno("Error interno en la transacción")
    finally:
        cursor.close()
        conexion.close()


@router.get("/mis-transacciones", response_model=list[TransaccionResponse])
def obtener_mis_transacciones(
    usuario_actual = Depends(get_usuario_actual)
):
    """
    Devuelve el historial de transacciones donde el usuario participó
    (ya sea como comprador o como vendedor).
    """
    usuario_id = usuario_actual["id"]

    conexion = get_db_connection()
    cursor = conexion.cursor()

    try:
        # El qr_token solo se le muestra al comprador. Si el vendedor lo viera,
        # podría liberar los fondos él solo sin encontrarse con nadie.
        cursor.execute('''
            SELECT id, publicacion_id, comprador_id, vendedor_id, monto, comision_plataforma,
                   id_pago_externo, estado_pago,
                   CASE WHEN comprador_id = %s THEN qr_token END,
                   fecha_creacion, fecha_liberacion
            FROM transacciones_escrow
            WHERE comprador_id = %s OR vendedor_id = %s
            ORDER BY fecha_creacion DESC;
        ''', (str(usuario_id), str(usuario_id), str(usuario_id)))

        transacciones_db = cursor.fetchall()

        # Mapeamos los resultados de la base de datos a un diccionario que Pydantic entienda
        resultado = []
        for t in transacciones_db:
            resultado.append({
                "id": t[0],
                "publicacion_id": t[1],
                "comprador_id": t[2],
                "vendedor_id": t[3],
                "monto": t[4],
                "comision_plataforma": t[5],
                "id_pago_externo": t[6],
                "estado_pago": t[7],
                "qr_token": t[8],
                "fecha_creacion": t[9],
                "fecha_liberacion": t[10]
            })

        return resultado

    except Exception as e:
        raise error_interno("Error al obtener el historial")
    finally:
        cursor.close()
        conexion.close()


@router.post("/liberar", status_code=status.HTTP_200_OK)
def liberar_fondos(
    datos: TransaccionLiberar,
    usuario_actual = Depends(get_usuario_actual)
):
    """
    Escaneo del QR.
    El vendedor envía el token del comprador para confirmar la entrega del artículo y liberar el dinero.
    """
    usuario_id = usuario_actual["id"]

    conexion = get_db_connection()
    cursor = conexion.cursor()

    try:
        # 1. Buscamos la transacción usando el token QR y la bloqueamos,
        # así una cancelación simultánea no puede pisar el escaneo (o al revés)
        cursor.execute('''
            SELECT t.id, t.vendedor_id, t.publicacion_id, t.estado_pago, p.tipo
            FROM transacciones_escrow t
            JOIN publicaciones p ON p.id = t.publicacion_id
            WHERE t.qr_token = %s
            FOR UPDATE OF t;
        ''', (str(datos.qr_token),))

        transaccion = cursor.fetchone()

        if not transaccion:
            raise HTTPException(status_code=404, detail="Código QR inválido o inexistente")

        transaccion_id, vendedor_id, publicacion_id, estado_actual, tipo = transaccion

        # 2. Barreras de Seguridad Estrictas
        if str(vendedor_id) != str(usuario_id):
            raise HTTPException(
                status_code=403,
                detail="Acceso denegado: Solo el vendedor de este artículo puede escanear el código QR"
            )

        if estado_actual != ESTADO_PARA_LIBERAR[tipo]:
            raise HTTPException(
                status_code=400,
                detail=f"La transacción no se puede liberar porque su estado actual es: {estado_actual}"
            )

        # === INICIO DE TRANSACCIÓN SQL ===

        # 3. Liberamos los fondos en la bóveda
        cursor.execute('''
            UPDATE transacciones_escrow
            SET estado_pago = 'liberado', fecha_liberacion = CURRENT_TIMESTAMP
            WHERE id = %s;
        ''', (str(transaccion_id),))

        # 4. Cambiamos el estado del artículo definitivamente a "vendido"
        cursor.execute('''
            UPDATE publicaciones
            SET estado = 'vendido'
            WHERE id = %s;
        ''', (str(publicacion_id),))

        # 5. Confirmamos los cambios
        conexion.commit()

        return {
            "status": "success",
            "message": "¡Escaneo exitoso! Artículo entregado y fondos liberados a tu cuenta."
        }

    except HTTPException:
        conexion.rollback()
        raise
    except Exception as e:
        conexion.rollback()
        raise error_interno("Error al liberar fondos")
    finally:
        cursor.close()
        conexion.close()


@router.post("/{id}/pago", status_code=status.HTTP_200_OK)
def iniciar_pago(
    id: UUID,
    usuario_actual: dict = Depends(get_usuario_actual)
):
    """
    Devuelve la URL de Mercado Pago (Checkout Pro) para pagar una compra pendiente.
    Se puede volver a llamar si el comprador cerró la ventana sin pagar.
    """
    conexion = get_db_connection()
    cursor = conexion.cursor()

    try:
        cursor.execute('''
            SELECT t.comprador_id, t.estado_pago, t.monto, p.tipo, p.titulo
            FROM transacciones_escrow t
            JOIN publicaciones p ON p.id = t.publicacion_id
            WHERE t.id = %s;
        ''', (str(id),))
        transaccion = cursor.fetchone()

        if not transaccion:
            raise HTTPException(status_code=404, detail="Transacción no encontrada")

        comprador_id, estado_actual, monto, tipo, titulo = transaccion

        if str(comprador_id) != str(usuario_actual["id"]):
            raise HTTPException(status_code=403, detail="Solo el comprador puede pagar esta operación")

        if tipo != 'venta':
            raise HTTPException(status_code=400, detail="Las donaciones no requieren pago")

        if estado_actual != 'pendiente':
            raise HTTPException(status_code=400, detail=f"La operación no se puede pagar en estado: {estado_actual}")

        try:
            url_pago = pagos.crear_preferencia(str(id), titulo, monto)
        except Exception as e:
            raise error_interno("Mercado Pago no respondió correctamente", 502)

        return {"url_pago": url_pago}

    finally:
        cursor.close()
        conexion.close()


def _cancelar(cursor, transaccion_id, publicacion_id, estado_actual, id_pago_externo) -> str:
    """
    Cancela una transacción y vuelve a poner el artículo en el catálogo.
    No hace commit: lo hace quien la llama. Devuelve el nuevo estado.
    Si Mercado Pago rechaza la devolución, lanza la excepción y no se toca la base.
    """
    # Si el pago ya estaba retenido hay que devolverlo; si no, no hay nada que devolver
    if estado_actual == 'retenido':
        pagos.reembolsar(id_pago_externo, f"reembolso-{transaccion_id}")
        nuevo_estado = 'reembolsado'
    else:
        nuevo_estado = 'cancelado'

    cursor.execute('''
        UPDATE transacciones_escrow SET estado_pago = %s WHERE id = %s;
    ''', (nuevo_estado, str(transaccion_id)))
    cursor.execute('''
        UPDATE publicaciones SET estado = 'disponible' WHERE id = %s;
    ''', (str(publicacion_id),))

    return nuevo_estado


@router.post("/{id}/cancelar", status_code=status.HTTP_200_OK)
def cancelar_transaccion(
    id: UUID,
    usuario_actual: dict = Depends(get_usuario_actual)
):
    """
    Cancela una operación que todavía no se concretó (no se escaneó el QR).
    Puede hacerlo cualquiera de las dos partes: sin escaneo no hubo entrega,
    así que el dinero vuelve al comprador y el artículo vuelve al catálogo.
    """
    usuario_id = usuario_actual["id"]

    conexion = get_db_connection()
    cursor = conexion.cursor()

    try:
        cursor.execute('''
            SELECT comprador_id, vendedor_id, publicacion_id, estado_pago, id_pago_externo
            FROM transacciones_escrow
            WHERE id = %s
            FOR UPDATE;
        ''', (str(id),))

        transaccion = cursor.fetchone()

        if not transaccion:
            raise HTTPException(status_code=404, detail="Transacción no encontrada")

        comprador_id, vendedor_id, publicacion_id, estado_actual, id_pago_externo = transaccion

        if str(usuario_id) not in (str(comprador_id), str(vendedor_id)):
            raise HTTPException(status_code=403, detail="Solo las partes involucradas pueden cancelar la operación")

        if estado_actual not in ('pendiente', 'retenido'):
            raise HTTPException(
                status_code=400,
                detail=f"La transacción no se puede cancelar porque su estado actual es: {estado_actual}"
            )

        try:
            nuevo_estado = _cancelar(cursor, id, publicacion_id, estado_actual, id_pago_externo)
        except Exception as e:
            raise error_interno("Mercado Pago no pudo procesar la devolución", 502)
        conexion.commit()

        return {"status": "success", "estado_pago": nuevo_estado, "message": "Operación cancelada"}

    except HTTPException:
        conexion.rollback()
        raise
    except Exception as e:
        conexion.rollback()
        raise error_interno("Error al cancelar")
    finally:
        cursor.close()
        conexion.close()


# Vercel Cron solo hace pedidos GET y se autentica con CRON_SECRET (ver vercel.json).
# Además de vencer operaciones, esta consulta diaria evita que Supabase pause el proyecto por inactividad.
@router.get("/vencer", status_code=status.HTTP_200_OK, dependencies=[Depends(requerir_cron)])
def vencer_transacciones():
    """
    Cancela (y reembolsa si corresponde) las operaciones vencidas:
    - ventas sin pagar después del plazo de pago,
    - cualquier operación sin escaneo después del plazo de encuentro.
    """
    conexion = get_db_connection()
    cursor = conexion.cursor()

    try:
        # ponytail: el plazo de encuentro se cuenta desde la creación, no desde la confirmación del pago (diferencia de horas)
        cursor.execute('''
            SELECT t.id, t.publicacion_id, t.estado_pago, t.id_pago_externo
            FROM transacciones_escrow t
            JOIN publicaciones p ON p.id = t.publicacion_id
            WHERE (p.tipo = 'venta' AND t.estado_pago = 'pendiente'
                   AND t.fecha_creacion < now() - make_interval(hours => %s))
               OR (t.estado_pago IN ('pendiente', 'retenido')
                   AND t.fecha_creacion < now() - make_interval(days => CASE p.tipo WHEN 'venta' THEN %s ELSE %s END))
            FOR UPDATE OF t;
        ''', (pagos.PLAZO_PAGO_HORAS, PLAZO_ENCUENTRO_DIAS['venta'], PLAZO_ENCUENTRO_DIAS['donacion']))

        vencidas = 0
        fallidas = 0
        for transaccion_id, publicacion_id, estado_actual, id_pago_externo in cursor.fetchall():
            try:
                _cancelar(cursor, transaccion_id, publicacion_id, estado_actual, id_pago_externo)
                vencidas += 1
            except Exception:
                # Si Mercado Pago rechaza una devolución, esa operación queda como estaba y se reintenta mañana
                fallidas += 1

        conexion.commit()

        return {"status": "success", "vencidas": vencidas, "fallidas": fallidas}

    except Exception as e:
        conexion.rollback()
        raise error_interno("Error al vencer transacciones")
    finally:
        cursor.close()
        conexion.close()


@router.get("/{id}/contacto", response_model=ContactoResponse, status_code=status.HTTP_200_OK)
def obtener_datos_contacto(
    id: UUID,
    usuario_actual: dict = Depends(get_usuario_actual)
):
    """
    Devuelve los datos de contacto de la otra parte involucrada en la transacción.
    Solo el comprador y el vendedor de esta orden tienen permiso para acceder,
    y en las ventas recién después de que el pago quedó retenido.
    """
    usuario_id = usuario_actual["id"]

    conexion = None
    cursor = None

    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()

        # 1. Buscamos la transacción para ver quiénes son los involucrados
        cursor.execute('''
            SELECT t.comprador_id, t.vendedor_id, t.estado_pago, p.tipo
            FROM transacciones_escrow t
            JOIN publicaciones p ON p.id = t.publicacion_id
            WHERE t.id = %s;
        ''', (str(id),))

        transaccion = cursor.fetchone()

        if not transaccion:
            raise HTTPException(status_code=404, detail="Transacción no encontrada")

        comprador_id, vendedor_id, estado_actual, tipo = transaccion

        # 2. Barrera de Privacidad: ¿El usuario que pregunta es parte de la transacción?
        if str(usuario_id) != str(comprador_id) and str(usuario_id) != str(vendedor_id):
            raise HTTPException(
                status_code=403,
                detail="Acceso denegado. Solo las partes involucradas pueden ver los datos de contacto."
            )

        # 3. Sin pago confirmado no se comparten datos: evita reservar solo para conseguir el teléfono
        if estado_actual not in ESTADOS_CON_CONTACTO[tipo]:
            raise HTTPException(
                status_code=400,
                detail=f"Los datos de contacto no están disponibles con la operación en estado: {estado_actual}"
            )

        # 4. Determinamos quién es la "contraparte"
        # Si yo soy el comprador, quiero los datos del vendedor. Y viceversa.
        contraparte_id = vendedor_id if str(usuario_id) == str(comprador_id) else comprador_id

        # 5. Buscamos los datos de contacto en la tabla de usuarios
        cursor.execute('''
            SELECT nombre, apellido, email, telefono
            FROM usuarios
            WHERE id = %s;
        ''', (str(contraparte_id),))

        datos_usuario = cursor.fetchone()

        if not datos_usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado en la base de datos")

        return {
            "nombre": datos_usuario[0],
            "apellido": datos_usuario[1],
            "email": datos_usuario[2],
            "telefono": datos_usuario[3]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise error_interno("Error al obtener los datos de contacto")
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()
