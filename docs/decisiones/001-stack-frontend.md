# 001 · Stack del frontend

**Fecha:** 02/11/2026 · **Estado:** Aceptada

## Contexto

El protocolo define una plataforma web responsiva con arquitectura cliente-servidor: frontend desplegado en Vercel y backend (FastAPI) en Render, con datos en Supabase. El hito 6 asigna 35 hs al frontend. Las pantallas obligatorias incluyen catálogo con filtros en cascada, publicación con fotos, generación y escaneo de códigos QR con la cámara del celular, pago y seguimiento de operaciones, y sesión con JWT.

## Opciones evaluadas

| Opción | A favor | En contra |
|---|---|---|
| React + Vite | Separación clara cliente/servidor, ecosistema más grande, librerías de QR maduras, valor laboral | Hay que elegir router y manejo de estado; sin SEO por defecto |
| Vue 3 + Vite | Curva de aprendizaje más suave, plantillas cercanas a HTML | Ecosistema más chico |
| Next.js | SEO del catálogo, deploy nativo en Vercel | Agrega un segundo servidor sobre FastAPI; más conceptos para 35 hs |
| FastAPI + Jinja2 + HTMX | Un solo proyecto y un solo deploy | Contradice la arquitectura del protocolo; duplica endpoints JSON/HTML |

## Decisión

**React + Vite**, desplegado como sitio estático en Vercel, consumiendo la API REST de FastAPI.

Piezas complementarias: Tailwind CSS para el diseño responsive, `qrcode.react` para mostrar el QR del comprador, `html5-qrcode` para escanearlo desde el navegador del vendedor (requiere HTTPS, provisto por Vercel), Supabase Storage para las imágenes.

### Actualización (09/11/2026)

- **Lenguaje: TypeScript.** El autor ya lo usa en otro proyecto, y los tipos ayudan a no equivocar los estados de una operación, de los que depende qué se muestra en cada pantalla.
- **Escaneo: `@yudiel/react-qr-scanner` en lugar de `html5-qrcode`.** La última versión publicada de `html5-qrcode` es de abril de 2023; la de `@yudiel/react-qr-scanner`, de mayo de 2026.
- **Sin librería para el acceso a la API ni para el estado global:** `fetch` y un contexto de React alcanzan para ocho pantallas. El navegador sube las fotos a la URL firmada que entrega el backend, así que tampoco hace falta el cliente de Supabase.
- **Administración mínima:** el protocolo marca el panel como opcional y la API ya cubre RF-12. Solo se hace la pantalla de solicitudes de colegios, que hace falta para el alta a pedido (RF-13).

## Consecuencias

- El backend necesita habilitar CORS para el dominio de Vercel (Sprint C).
- El SEO del catálogo queda fuera del alcance del prototipo; no es un objetivo del protocolo.
