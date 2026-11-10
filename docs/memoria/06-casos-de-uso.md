# 06 · Casos de uso

> Borrador. Cada caso se relaciona con los requerimientos del [capítulo 01](01-requerimientos.md).

## Diagrama

![Diagrama de casos de uso](diagramas/casos-de-uso.svg)

| Código | Caso de uso | Actores | Requerimientos |
|---|---|---|---|
| CU-01 | Registrarse | Visitante | RF-01 |
| CU-02 | Iniciar sesión | Visitante | RF-01 |
| CU-03 | Explorar el catálogo | Visitante, Comprador | RF-03 |
| CU-04 | Publicar un artículo | Vendedor | RF-02 |
| CU-05 | Pedir el alta de un colegio | Vendedor | RF-13 |
| CU-06 | Gestionar las publicaciones propias | Vendedor | RF-04, RF-13 |
| CU-07 | Reservar un artículo | Comprador | RF-05 |
| CU-08 | Pagar la reserva | Comprador, Mercado Pago | RF-06 |
| CU-09 | Ver los datos de contacto | Comprador, Vendedor | RF-08 |
| CU-10 | Mostrar el código QR de entrega | Comprador | RF-07 |
| CU-11 | Confirmar la entrega escaneando el QR | Vendedor | RF-07 |
| CU-12 | Cancelar una operación | Comprador, Vendedor, Mercado Pago | RF-09 |
| CU-13 | Consultar las operaciones | Comprador, Vendedor | RF-11 |
| CU-14 | Vencer las operaciones | Vercel Cron, Mercado Pago | RF-10 |
| CU-15 | Gestionar las instituciones | Administrador | RF-12 |
| CU-16 | Resolver una solicitud de colegio | Administrador | RF-13 |

## Especificación de los casos principales

### CU-03 · Explorar el catálogo

**Actores:** Visitante, Comprador.
**Precondiciones:** ninguna.

**Flujo principal**

1. En la primera visita, el actor elige su provincia, localidad y colegio. El sistema guarda la elección en el navegador.
2. El sistema muestra los primeros 20 artículos disponibles que coinciden con la ubicación elegida.
3. El actor combina filtros por provincia, ciudad, institución, categoría, tipo y talle.
4. El sistema actualiza la lista. Al llegar al final, carga el bloque siguiente.
5. El actor abre el detalle de un artículo.

**Flujos alternativos**

- 4a. Ningún artículo coincide: el sistema informa que no hay artículos con esos filtros.

**Postcondiciones:** no cambia ningún dato. Solo se listan publicaciones en estado `disponible`.

### CU-04 · Publicar un artículo

**Actores:** Vendedor.
**Precondiciones:** el actor inició sesión. Si no, el sistema se lo pide y vuelve a esta pantalla.

**Flujo principal**

1. El actor carga título, categoría, talle y tipo (venta o donación). Si es una venta, indica el precio.
2. El actor agrega hasta 5 fotos. El sistema las reduce y las sube al almacenamiento con una URL firmada.
3. El actor elige provincia, localidad y colegio.
4. El sistema valida los datos, crea la publicación en estado `disponible` y la muestra en el catálogo.

**Flujos alternativos**

- 3a. El colegio no está en la lista: se ejecuta CU-05.
- 4a. El precio no corresponde al tipo: el sistema rechaza la publicación e informa el motivo (RN-01).
- 4b. Alguna foto no fue subida por el actor: el sistema rechaza la publicación (RN-14).

**Postcondiciones:** existe una publicación del actor, visible en el catálogo salvo que espere el alta de un colegio.

### CU-05 · Pedir el alta de un colegio

**Extiende a:** CU-04.
**Actores:** Vendedor.
**Precondiciones:** el actor está publicando y su colegio no aparece en la lista.

**Flujo principal**

1. El actor escribe el nombre del colegio.
2. El sistema crea la publicación en estado `pendiente_colegio` y una solicitud para el administrador.
3. El sistema le informa al actor que la publicación espera el alta del colegio.

**Postcondiciones:** la publicación no aparece en el catálogo ni se puede reservar hasta resolver la solicitud (RN-15).

### CU-07 · Reservar un artículo

**Actores:** Comprador.
**Precondiciones:** el actor inició sesión. El artículo está `disponible`.

**Flujo principal**

1. El actor pide reservar el artículo desde su detalle.
2. El sistema bloquea la publicación y verifica que siga disponible y que no sea del actor.
3. El sistema crea la operación en estado `pendiente`, con el precio congelado y la comisión calculada (5 % en ventas, 0 en donaciones).
4. El sistema marca la publicación como `reservado`.
5. Si es una venta, el flujo sigue en CU-08. Si es una donación, el actor ya puede ver el QR (CU-10) y el contacto (CU-09).

**Flujos alternativos**

- 2a. El artículo ya fue reservado por otra persona: el sistema lo informa y no crea la operación (RN-03).
- 2b. El artículo es del actor: el sistema rechaza la reserva (RN-02).
- 2c. Es una donación y el actor ya tiene 3 pendientes: el sistema rechaza la reserva (RN-12).

**Postcondiciones:** el artículo deja de verse en el catálogo y existe una operación `pendiente`.

### CU-08 · Pagar la reserva

**Actores:** Comprador, Mercado Pago.
**Precondiciones:** existe una venta `pendiente` del actor.

**Flujo principal**

1. El actor elige pagar.
2. El sistema crea una preferencia de pago con vencimiento a 24 horas y redirige al actor a Mercado Pago.
3. El actor paga en Mercado Pago y vuelve a la plataforma, que le indica que está confirmando el pago.
4. Mercado Pago envía un aviso firmado al sistema.
5. El sistema verifica la firma y consulta el pago a Mercado Pago.
6. Con el pago aprobado, la operación pasa a `retenido`.
7. La pantalla del actor se actualiza y muestra el QR y el contacto.

**Flujos alternativos**

- 3a. El actor cierra la ventana sin pagar: puede volver a intentarlo mientras la reserva siga vigente.
- 5a. La firma no es válida: el sistema rechaza el aviso y no cambia nada (RNF-07).
- 5b. El mismo aviso llega más de una vez: la segunda vez no tiene efecto (RNF-07).
- 6a. El pago llega cuando la operación ya estaba cancelada: el sistema devuelve el dinero y la operación pasa a `reembolsado`.

**Postcondiciones:** el pago queda retenido hasta el escaneo. El vendedor todavía no dispone de los fondos.

### CU-11 · Confirmar la entrega escaneando el QR

**Actores:** Vendedor.
**Precondiciones:** el actor inició sesión. Está junto al comprador, que muestra el QR (CU-10). La operación está `retenido` en una venta o `pendiente` en una donación.

**Flujo principal**

1. El actor abre el escáner desde la operación y apunta la cámara al QR del comprador.
2. El sistema busca la operación por el código y la bloquea.
3. El sistema verifica que el actor sea el vendedor y que el estado permita escanear.
4. La operación pasa a `liberado` y la publicación a `vendido`.
5. Las pantallas de ambas partes muestran la entrega confirmada.

**Flujos alternativos**

- 2a. El código no existe: el sistema informa que es inválido.
- 3a. El actor no es el vendedor de esa operación: el sistema rechaza el escaneo (RN-05).
- 3b. El pago no está retenido o la operación ya terminó: el sistema rechaza el escaneo (RN-06).

**Postcondiciones:** la entrega queda confirmada y la operación ya no se puede cancelar (RN-07).

### CU-12 · Cancelar una operación

**Actores:** Comprador, Vendedor, Mercado Pago.
**Precondiciones:** el actor es parte de la operación, que está `pendiente` o `retenido`.

**Flujo principal**

1. El actor pide cancelar y confirma.
2. El sistema bloquea la operación.
3. Si el pago estaba retenido, el sistema pide la devolución a Mercado Pago.
4. La operación pasa a `reembolsado` si había pago o a `cancelado` si no lo había.
5. La publicación vuelve a `disponible`.

**Flujos alternativos**

- 3a. Mercado Pago rechaza la devolución: la operación queda como estaba y el sistema informa el error.

**Postcondiciones:** el artículo vuelve al catálogo y el QR de la operación deja de servir.

### CU-14 · Vencer las operaciones

**Actores:** Vercel Cron, Mercado Pago.
**Precondiciones:** la tarea se autentica con la clave secreta. Se ejecuta una vez por día.

**Flujo principal**

1. El sistema busca las ventas sin pagar con más de 24 horas y las operaciones sin escaneo con más de 7 días (4 en donaciones).
2. Para cada una, ejecuta la misma cancelación de CU-12.
3. El sistema informa cuántas venció y cuántas fallaron.

**Flujos alternativos**

- 2a. Mercado Pago rechaza una devolución: esa operación queda como estaba y se reintenta al día siguiente.

**Postcondiciones:** las operaciones vencidas quedan cerradas y sus artículos vuelven al catálogo.

### CU-16 · Resolver una solicitud de colegio

**Actores:** Administrador.
**Precondiciones:** el actor inició sesión con rol de administrador. Hay una solicitud `pendiente`.

**Flujo principal**

1. El actor abre el panel de solicitudes y revisa una.
2. El actor acepta el colegio.
3. El sistema crea la institución, le asigna la publicación y la pasa a `disponible`.

**Flujos alternativos**

- 2a. El colegio ya existía con otro nombre: el actor indica cuál es. El sistema asigna ese colegio, publica el artículo y le avisa al dueño.
- 2b. El colegio no existe: el actor lo rechaza. La publicación queda en `borrador` con un aviso, y su dueño puede elegir otro colegio (CU-06).
- 3a. El dueño dio de baja la publicación mientras esperaba: la solicitud se resuelve, pero la publicación sigue dada de baja.

**Postcondiciones:** la solicitud queda resuelta y no se puede resolver dos veces.

## Casos de uso secundarios

| Código | Resumen |
|---|---|
| CU-01 | El visitante carga sus datos. El sistema valida el correo y la contraseña (8 caracteres o más), crea la cuenta e inicia la sesión. |
| CU-02 | El visitante ingresa correo y contraseña y recibe una sesión de 2 horas. Después de 5 intentos fallidos, la cuenta se bloquea 15 minutos. |
| CU-06 | El vendedor ve sus publicaciones y su estado, da de baja las que no tienen una operación en curso, y elige otro colegio si su solicitud fue rechazada. |
| CU-09 | Cada parte ve el nombre, el correo y el teléfono de la otra, con el pago retenido en las ventas o desde la reserva en las donaciones. |
| CU-10 | El comprador ve su QR en los estados en los que se puede escanear. Mientras lo muestra, la pantalla consulta el estado cada 5 segundos. |
| CU-13 | El usuario ve sus operaciones como comprador y como vendedor, con el artículo y el estado. |
| CU-15 | El administrador crea, edita y borra instituciones. Hoy se hace por la API, sin pantalla propia. No se puede borrar una institución con publicaciones. |
