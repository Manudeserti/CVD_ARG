# 002 · Retención de fondos

**Fecha:** 02/11/2026 · **Estado:** Aceptada para el prototipo · a revisar con el director

## Contexto

El protocolo establece que el módulo transaccional "retendrá los fondos hasta la confirmación de entrega del producto". Es la innovación central del proyecto.

Si la plataforma cobra al comprador en su propia cuenta y después paga al vendedor, custodia fondos de terceros. En Argentina esa actividad puede encuadrar en:

- **BCRA – Proveedores de Servicios de Pago (PSP):** inscripción obligatoria en el registro para operar; si se mantienen fondos de clientes, deben estar disponibles en todo momento y depositados en cuentas a la vista en bancos del país (Com. "A" 6859 y modificatorias, la última relevada es la "A" 8432 de mayo 2026).
- **UIF:** la Ley 27.739 incorporó a los proveedores de servicios de cobros y/o pagos como sujetos obligados; la Resolución UIF 200/2024 exige un sistema de prevención de lavado (identificación de clientes, oficial de cumplimiento, reportes).
- **Impuestos y consumidor:** posibles regímenes de retención (ARCA, Ingresos Brutos) y responsabilidad como intermediario ante la Ley 24.240.

Esto es un relevamiento general, no asesoramiento legal.

## Opciones evaluadas

| Opción | Fiel al protocolo | Riesgo regulatorio | Comentario |
|---|---|---|---|
| Retención propia (la plataforma cobra y libera) | Sí | Alto en producción, nulo en sandbox | Reembolsos siempre posibles: el saldo lo tiene la plataforma |
| Split de pagos de Mercado Pago (marketplace) | Parcial | Bajo: Mercado Pago es el PSP | La plataforma no controla cuándo se libera el dinero; el QR pasa a ser solo confirmación |
| Reserva de valores de Mercado Pago (autorizar y capturar) | Sí | Bajo | Captura en Argentina dentro de 7 días; requiere Checkout API; verificar medios de pago y combinación con split |

## Decisión

El prototipo implementa la **retención propia** tal como la describe el protocolo, en el **sandbox de Mercado Pago**, con credenciales y usuarios de prueba. Durante el trabajo final no se opera con dinero real ni con público real.

Reglas de negocio derivadas:

- El escaneo del QR es la única prueba de entrega. Sin escaneo, el dinero vuelve al comprador.
- Cualquiera de las partes puede cancelar mientras no se haya escaneado el QR.
- Plazo de encuentro: 7 días. Vencido sin escaneo, la operación se cancela y se reembolsa automáticamente.
- El vendedor escanea el QR antes de entregar el artículo.

## Consecuencias

- La máquina de estados es la misma para las tres opciones; migrar a producción cambia solo las llamadas a Mercado Pago (reembolsar ↔ cancelar reserva, liberar ↔ capturar).
- La memoria incluye un capítulo de consideraciones regulatorias y camino a producción (Sprint B).
- Antes de operar con dinero real: consulta legal e inscripción como PSP, o migración a reserva de valores / split.
