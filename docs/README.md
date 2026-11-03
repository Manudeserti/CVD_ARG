# Documentación del Trabajo Final

La memoria y los manuales se escriben a lo largo del proyecto, no al final. Cada sprint cierra con su parte.

## Memoria (`memoria/`)

| Capítulo | Sprint | Estado |
|---|---|---|
| [01 · Requerimientos](memoria/01-requerimientos.md) | A | Borrador |
| [02 · Modelo de datos y estados](memoria/02-modelo-de-datos.md) | A | Borrador |
| [03 · Arquitectura y flujo de pago](memoria/03-arquitectura-y-pagos.md) | B | Borrador |
| [04 · Consideraciones regulatorias y camino a producción](memoria/04-regulatorio-y-produccion.md) | B | Borrador |
| 05 · Pruebas | D | Pendiente |

## Manuales (`manuales/`)

| Manual | Sprint | Estado |
|---|---|---|
| Manual de usuario (con capturas) | C | Pendiente |
| [Manual técnico de instalación y despliegue](manuales/manual-tecnico.md) | B / D | Borrador |

## Horas (`horas.csv`)

Registro de horas reales por actividad, para comparar con lo estimado en el protocolo: 1 Requerimientos (20 hs), 2 Arquitectura y modelo de datos (30), 3 Backend y API (40), 4 Módulo transaccional (25), 5 Validación QR (20), 6 Frontend (35), 7 Testing y despliegue (20), 8 Memoria y manuales (10). Total: 200 hs.

Las filas de agosto se reconstruyeron a partir de los commits (1,5 h antes del primer commit de cada sesión más la duración entre commits); son un piso. Las del 02/11 salen de los horarios registrados de las sesiones de trabajo.

## Decisiones (`decisiones/`)

Registro corto de cada decisión importante: contexto, opciones, decisión y consecuencias. Se trasladan casi directo a la memoria.

- [001 · Stack del frontend](decisiones/001-stack-frontend.md)
- [002 · Retención de fondos](decisiones/002-retencion-de-fondos.md)
- [003 · Backend en Vercel en lugar de Render](decisiones/003-backend-en-vercel.md)
