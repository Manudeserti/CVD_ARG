from fastapi import APIRouter, Depends, HTTPException, status
from decimal import Decimal
from uuid import UUID
from schemas.transaccion_schema import TransaccionCreate, TransaccionResponse
from database.database import get_db_connection
from utils.security import get_usuario_actual

router = APIRouter(
    prefix="/api/transacciones",
    tags=["Transacciones (Escrow)"]
)

@router.post("/", response_model=TransaccionResponse, status_code=status.HTTP_201_CREATED)
def iniciar_transaccion(
    compra: TransaccionCreate, 
    usuario_actual = Depends(get_usuario_actual) # ¡La barrera VIP!
):
    """
    Inicia el proceso de compra (Escrow).
    Valida el stock, congela el precio, calcula la comisión y reserva el artículo.
    """
    # Extraemos el ID del comprador del token JWT. 
    # (Si en tu security.py el usuario es un diccionario, cambiá esto por usuario_actual['id'])
    comprador_id = usuario_actual["id"] 
    
    PORCENTAJE_COMISION = Decimal('0.05') # 5% de comisión para la plataforma

    conexion = get_db_connection()
    cursor = conexion.cursor()

    try:
        # 1. Buscamos el artículo en la base de datos real
        cursor.execute('''
            SELECT vendedor_id, precio, estado, tipo
            FROM publicaciones 
            WHERE id = %s;
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

        # 3. Cálculos financieros
        comision_calculada = precio_original * PORCENTAJE_COMISION

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
        
        # 7. Armamos la respuesta mapeando lo que devolvió el RETURNING
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
        raise HTTPException(status_code=500, detail=f"Error interno en la transacción: {str(e)}")
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
        # Buscamos el historial y lo ordenamos desde el más reciente al más antiguo
        cursor.execute('''
            SELECT id, publicacion_id, comprador_id, vendedor_id, monto, comision_plataforma, 
                   id_pago_externo, estado_pago, qr_token, fecha_creacion, fecha_liberacion
            FROM transacciones_escrow
            WHERE comprador_id = %s OR vendedor_id = %s
            ORDER BY fecha_creacion DESC;
        ''', (str(usuario_id), str(usuario_id)))
        
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
        raise HTTPException(status_code=500, detail=f"Error al obtener el historial: {str(e)}")
    finally:
        cursor.close()
        conexion.close()


from schemas.transaccion_schema import TransaccionLiberar

@router.post("/liberar", status_code=status.HTTP_200_OK)
def liberar_fondos(
    datos: TransaccionLiberar,
    usuario_actual = Depends(get_usuario_actual)
):
    """
    Simula el escaneo del QR. 
    El vendedor envía el token del comprador para confirmar la entrega del artículo y liberar el dinero.
    """
    usuario_id = usuario_actual["id"]
    
    conexion = get_db_connection()
    cursor = conexion.cursor()

    try:
        # 1. Buscamos la transacción usando el token QR
        cursor.execute('''
            SELECT id, vendedor_id, publicacion_id, estado_pago 
            FROM transacciones_escrow 
            WHERE qr_token = %s;
        ''', (str(datos.qr_token),))
        
        transaccion = cursor.fetchone()

        if not transaccion:
            raise HTTPException(status_code=404, detail="Código QR inválido o inexistente")
            
        transaccion_id, vendedor_id, publicacion_id, estado_actual = transaccion

        # 2. Barreras de Seguridad Estrictas
        if str(vendedor_id) != str(usuario_id):
            raise HTTPException(
                status_code=403, 
                detail="Acceso denegado: Solo el vendedor de este artículo puede escanear el código QR"
            )
            
        if estado_actual != 'pendiente': # (En un futuro con MercadoPago, acá diría 'retenido')
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
        raise HTTPException(status_code=500, detail=f"Error al liberar fondos: {str(e)}")
    finally:
        cursor.close()
        conexion.close()