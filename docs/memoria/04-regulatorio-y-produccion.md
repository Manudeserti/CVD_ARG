# 04 · Consideraciones regulatorias y camino a producción

> Borrador. Decisiones relacionadas: [002](../decisiones/002-retencion-de-fondos.md), [003](../decisiones/003-backend-en-vercel.md).

## Marco regulatorio

La innovación central del proyecto es retener el dinero del comprador hasta que el vendedor escanea el QR en el encuentro. Si la plataforma cobra en su propia cuenta y después le paga al vendedor, custodia fondos de terceros. En Argentina eso puede encuadrar en:

| Ámbito | Norma | Qué exige |
|---|---|---|
| BCRA | Registro de Proveedores de Servicios de Pago (Com. "A" 6859 y modificatorias) | Inscripción para operar; los fondos de clientes deben estar disponibles en todo momento, en cuentas a la vista en bancos del país |
| UIF | Ley 27.739 y Resolución UIF 200/2024 | Los proveedores de servicios de cobros y pagos son sujetos obligados: identificación de clientes, oficial de cumplimiento, reportes de operaciones sospechosas |
| Impuestos | ARCA, Ingresos Brutos | Posibles regímenes de retención sobre las comisiones y los cobros |
| Consumidor | Ley 24.240 | Responsabilidad como intermediario en la operación |

Es un relevamiento general, no asesoramiento legal. Por eso el prototipo funciona en el entorno de pruebas de Mercado Pago, con credenciales y cuentas de prueba, sin dinero ni público real (ver decisión 002).

## Qué hace Mercado Pago con el dinero

Al consultar los pagos de prueba a la API se observó que Mercado Pago no le acredita el dinero al vendedor en el momento: el pago queda aprobado, pero con `money_release_status: pending` y una fecha de liberación unos 18 días posterior. Es decir, Mercado Pago ya aplica su propia retención antes de que el dinero esté disponible.

Dos consecuencias para el diseño:

- El plazo de encuentro de la plataforma (7 días) termina antes de esa liberación, así que las devoluciones por cancelación o vencimiento ocurren mientras Mercado Pago todavía retiene el dinero.
- Refuerza la alternativa de apoyarse en los mecanismos de Mercado Pago (split de pagos o reserva de valores) en lugar de custodiar fondos propios en producción.

El plazo de liberación depende de la configuración de la cuenta y del medio de pago; el valor observado corresponde a las cuentas de prueba usadas.

## Pruebas contra Mercado Pago

### Entorno de pruebas (2 y 3 de noviembre de 2026)

Con el backend desplegado en Vercel, usuarios de la plataforma de prueba y cuentas de prueba de Mercado Pago:

| Paso | Resultado |
|---|---|
| Crear el link de pago (preferencia de Checkout Pro) | Correcto |
| Pagar con la cuenta compradora de prueba | Correcto |
| Webhook firmado: la operación pasa a `retenido` con el id del pago | Correcto |
| Webhook sin firma | Rechazado (401) |
| Contacto de la contraparte después del pago | Correcto |
| El comprador intenta escanear su propio QR | Rechazado (403) |
| El vendedor escanea el QR: la operación pasa a `liberado` y el artículo a `vendido` | Correcto |
| Cancelar después del escaneo | Rechazado (400) |
| **Cancelar una operación pagada (devolución)** | **Rechazado por Mercado Pago** |

Mercado Pago rechazó todas las devoluciones con:

```
401 · Unauthorized use of live credentials
```

Se descartaron, una por una, estas causas:

| Variante | Resultado |
|---|---|
| Pago con saldo de la cuenta compradora de prueba | 401 |
| Pago con tarjeta de prueba, con sesión de la cuenta compradora | 401 |
| Pago con tarjeta de prueba como invitado, sin cuenta de prueba | 401 |
| Credenciales de prueba de la aplicación | 401 |
| Credenciales de producción de la cuenta vendedora de prueba | 401 |
| Saldo disponible cargado en la cuenta vendedora | 401 |
| Pedido de devolución varios minutos después del pago | 401 (el error es de permisos, no de tiempos) |

La documentación oficial, consultada también con el servidor MCP de Mercado Pago, no menciona este error para devoluciones. Conclusión: con Checkout Pro y cuentas de prueba, el entorno de pruebas no permite probar devoluciones.

En los tres casos rechazados, el backend respondió error (502) y no modificó la base: la operación siguió `retenido` y el artículo reservado. Es el comportamiento buscado con la regla "primero Mercado Pago, después la base" (capítulo 03): el sistema nunca registra una devolución que no ocurrió.

### Verificación con dinero real (3 de noviembre de 2026)

Para comprobar que el problema era del entorno de pruebas y no del código, se hizo una única operación real, fuera del backend desplegado:

1. Con las credenciales de producción de la cuenta del autor se creó un link de pago por $100.
2. Pagó otra persona, con su propia cuenta.
3. Se pidió la devolución con la misma llamada que usa el backend (`POST /v1/payments/{id}/refunds` con clave de idempotencia).

Mercado Pago respondió `201`, devolución aprobada por $100, y el pago quedó en estado `refunded`. La llamada de devolución del backend funciona contra Mercado Pago real.

Esta operación es una excepción controlada a la decisión 002: dinero propio, entre personas conocidas, devuelto en el acto, y sin pasar por la plataforma.

### Cobertura automática

El resto de los caminos de devolución (cancelación con pago retenido, pago tardío de una reserva vencida, vencimiento a los 7 días) están cubiertos por los tests automáticos, que simulan las respuestas de Mercado Pago (capítulo 05).

## Camino a producción

Antes de operar con dinero y usuarios reales:

1. **Definir el modelo de cobro**, con asesoramiento legal:
   - **Retención propia:** requiere inscripción como PSP en el BCRA y el sistema de prevención de lavado de la UIF.
   - **Reserva de valores de Mercado Pago:** se autoriza el pago y se captura al escanear el QR. Requiere migrar a Checkout API, y la captura en Argentina tiene que hacerse dentro de los 7 días, que coincide con el plazo de encuentro.
   - **Split de pagos (marketplace):** Mercado Pago es quien custodia y reparte; la plataforma no controla el momento de la liberación y el QR pasa a ser solo una confirmación.

   La máquina de estados es la misma en los tres casos: cambian solo las llamadas a Mercado Pago (devolver ↔ cancelar la reserva, liberar ↔ capturar).
2. **Activar las credenciales de producción** de la aplicación y reemplazar las de prueba en Vercel.
3. **Configurar el webhook de producción** en Mercado Pago y su clave secreta.
4. **Pasar Vercel al plan Pro**, porque el plan gratuito es solo para uso no comercial.
5. **Transferir al vendedor** al liberar: en el prototipo, liberar es solo un cambio de estado (decisión 002).
