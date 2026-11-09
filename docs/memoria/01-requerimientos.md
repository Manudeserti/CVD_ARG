# 01 · Requerimientos

> Borrador. Basado en el protocolo final (presentado el 09/09/2026) y en las decisiones [001](../decisiones/001-stack-frontend.md) y [002](../decisiones/002-retencion-de-fondos.md).

## Actores

- **Usuario:** cualquier persona registrada. Puede publicar (vendedor/donante) y comprar o recibir (comprador/receptor). Un mismo usuario cumple ambos roles en distintas operaciones.
- **Visitante:** persona sin sesión. Solo puede navegar el catálogo.
- **Administrador:** gestiona el listado de instituciones y ejecuta tareas de mantenimiento.
- **Mercado Pago:** sistema externo que procesa los pagos (sandbox en el prototipo).

## Requerimientos funcionales del prototipo

| Código | Requerimiento | Estado |
|---|---|---|
| RF-01 | Registro e inicio de sesión con correo y contraseña | Hecho |
| RF-02 | Publicar artículos de tipo venta (precio > 0) o donación (sin precio), con categoría, talle, institución e imágenes | Backend hecho; pantalla en Sprint C |
| RF-03 | Catálogo público con filtros combinables: provincia, ciudad, institución, categoría, tipo y talle | Hecho |
| RF-04 | Ver y dar de baja las publicaciones propias | Hecho |
| RF-05 | Iniciar una compra o solicitud de donación, que reserva el artículo | Hecho |
| RF-06 | Pagar mediante billetera virtual; los fondos quedan retenidos y se cobra una comisión del 5% en las ventas | Hecho (probado en sandbox; devolución verificada con dinero real, ver cap. 04) |
| RF-07 | Generar un código QR para el comprador; el vendedor lo escanea en el encuentro y se liberan los fondos | Backend hecho; pantalla en Sprint C |
| RF-08 | Compartir los datos de contacto de la contraparte una vez confirmado el pago | Hecho |
| RF-09 | Cancelar una operación no concretada, con reembolso si había pago | Hecho |
| RF-10 | Vencer automáticamente las reservas sin pagar (24 h) y las operaciones sin escaneo (7 días) | Hecho |
| RF-11 | Historial de operaciones del usuario | Hecho |
| RF-12 | Alta, edición y baja de instituciones por un administrador | Hecho |

## Funcionalidades opcionales (fuera del núcleo)

Instituciones por demanda, alertas automáticas por correo, panel de administración con reclamos, calificación y reputación. Fuera de alcance: envíos por correo y pagos fuera de las billeteras virtuales.

## Reglas de negocio

| Código | Regla |
|---|---|
| RN-01 | Una venta tiene precio mayor a 0; una donación no tiene precio ni comisión. |
| RN-02 | Un usuario no puede comprar su propio artículo. |
| RN-03 | Un artículo reservado no puede ser tomado por otro comprador, incluso si dos lo intentan al mismo tiempo. |
| RN-04 | El código QR solo lo ve el comprador. El vendedor nunca tiene acceso a él. |
| RN-05 | Solo el vendedor de la operación puede escanear el QR. |
| RN-06 | En una venta, el QR solo se puede escanear con el pago retenido. En una donación, desde que se inicia la operación. |
| RN-07 | El escaneo del QR es la única prueba de entrega. Una vez escaneado, la operación no se puede cancelar. |
| RN-08 | Sin escaneo, cualquiera de las partes puede cancelar y el dinero vuelve al comprador. |
| RN-09 | Si pasan 7 días sin escaneo (4 en las donaciones), la operación se cancela y, si había pago, se reembolsa automáticamente. Una venta reservada y no pagada se libera a las 24 horas. |
| RN-10 | Los datos de contacto se comparten recién con el pago retenido (ventas) o con la operación iniciada (donaciones). |
| RN-11 | Una publicación con una operación en curso no se puede dar de baja. |
| RN-12 | Un usuario puede tener como máximo 3 donaciones pendientes de retirar a la vez. Las ventas no tienen tope. |
| RN-13 | Una venta tiene precio mayor a 0 y una donación precio 0; la base de datos lo garantiza con una restricción. |
| RN-14 | Una publicación tiene como máximo 5 fotos (JPG, PNG o WebP, hasta 5 MB cada una), y todas tienen que haber sido subidas por su autor. |

## Requerimientos no funcionales

- **Seguridad:** contraseñas con bcrypt; sesiones con JWT firmado (HS256, vencimiento 2 h); rutas privadas protegidas; operaciones administrativas restringidas por rol; bloqueo de la cuenta por 15 minutos tras 5 intentos de login fallidos; los errores internos no exponen detalles al cliente (quedan en los logs).
- **Consistencia:** los cambios de estado de dinero y artículos se hacen en una única transacción de base de datos con bloqueo de fila.
- **Usabilidad:** interfaz responsive pensada primero para celular, porque el escaneo ocurre en el encuentro presencial.
- **Costo:** infraestructura en planes gratuitos (Supabase y Vercel).
