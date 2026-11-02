# 003 · Backend en Vercel en lugar de Render

**Fecha:** 02/11/2026 · **Estado:** Aceptada

## Contexto

El protocolo menciona Supabase, Vercel y Render como plataformas de despliegue. La restricción del proyecto es no gastar dinero. Al revisar los planes gratuitos (noviembre 2026):

- **Render (gratis):** el servicio se duerme a los 15 minutos sin tráfico y tarda alrededor de un minuto en volver. No incluye tareas programadas.
- **Vercel Hobby (gratis, uso no comercial):** ejecuta aplicaciones FastAPI como funciones de Python sin configuración especial (detecta `main.py` con la variable `app`) e incluye tareas programadas (cron) de hasta una ejecución diaria.
- **Supabase (gratis):** pausa el proyecto después de una semana sin consultas a la base. Un proyecto pausado se puede restaurar durante 90 días.

## Decisión

El backend se despliega en **Vercel**, como un proyecto separado del frontend con directorio raíz `backend/`.

Una tarea programada diaria (`vercel.json`) llama a `GET /api/transacciones/vencer`, autenticada con `CRON_SECRET`. Esa única tarea cumple dos funciones:

1. Vence las reservas sin pagar (24 h) y las operaciones sin encuentro (7 días), con reembolso si corresponde.
2. Consulta la base todos los días, así Supabase nunca llega a la semana de inactividad que pausa el proyecto.

## Consecuencias

- Toda la infraestructura queda en dos plataformas (Vercel y Supabase), sin costo.
- Las funciones arrancan en frío tras un rato sin uso, pero en segundos y no en un minuto.
- Las conexiones a la base se abren por pedido; se usa el *Transaction pooler* de Supabase (puerto 6543), pensado para este caso.
- El plan Hobby de Vercel es solo para uso no comercial. Si la plataforma pasara a cobrar comisiones reales, habría que pasar al plan Pro.
- La tarea diaria tiene precisión de una hora: puede ejecutarse en cualquier momento entre las 9:00 y las 9:59 UTC. Para plazos de 24 horas y 7 días no es un problema.
