# 08 · Plan de pruebas

> Borrador. Este capítulo define qué se prueba y cómo. Los resultados de la ejecución final van en el capítulo de resultados del informe.

## Alcance

Se verifican los requerimientos funcionales RF-01 a RF-13, las reglas de negocio RN-01 a RN-16 y los requerimientos no funcionales que se pueden medir. Se valida la plataforma publicada con el circuito real de pago en el entorno de pruebas de Mercado Pago. No se prueba el comportamiento con dinero real a escala, por la restricción R-02.

## Tipos de prueba

| Nivel | Qué verifica | Herramienta | Automatizada |
|---|---|---|---|
| Integración de API | Reglas de negocio, permisos y transacciones contra una base PostgreSQL real | pytest con FastAPI TestClient (`backend/tests/test_flujo.py`) | Sí |
| Sistema (punta a punta) | Recorrido completo por la interfaz, con varios usuarios a la vez | playwright-core y Chrome (`frontend/e2e/flujo.mjs`) | Sí |
| Integración externa | Pago, webhook y devolución contra Mercado Pago | Manual, sobre el sistema publicado | No |
| Aceptación en dispositivos reales | Pago y escaneo con la cámara entre dos celulares | Manual | No |
| Seguridad | Accesos no autorizados, firmas falsas y validación de archivos | Incluida en las pruebas de API | Sí |
| Rendimiento | Tiempo de respuesta del catálogo | A definir | Pendiente |
| Evaluación con usuarios | Que personas ajenas al desarrollo completen el circuito | Observación y cuestionario | Pendiente |

No se escribieron pruebas unitarias aisladas: casi toda la lógica está en transacciones SQL, y probarla sin una base real no comprobaría el bloqueo de filas ni las restricciones.

## Criterios de selección

Se priorizan los escenarios en los que un error implica perder dinero o entregar un artículo sin garantía. Para cada regla se prueba el camino válido y al menos un camino prohibido: quién no puede hacerlo, en qué estado no se puede y qué dato no se acepta. También se incluyen los reintentos y los casos fuera de orden que produce un sistema de pagos, como avisos repetidos o pagos tardíos.

## Entornos

| Entorno | Componentes | Uso |
|---|---|---|
| Local de pruebas | PostgreSQL en Docker (puerto 5433), backend y frontend locales; Mercado Pago y Storage simulados | Pruebas automáticas. Se puede borrar sin riesgo |
| Publicado | Vercel, Supabase y Mercado Pago sandbox | Pruebas manuales de pago y escaneo |
| Dinero real | Cuenta de Mercado Pago real, solo llamadas puntuales | Verificar la devolución, que el sandbox no permite probar (capítulo 04) |
| Dispositivos | Chrome en PC y dos celulares reales | Cámara, interfaz y flujo entre dos personas |

Las pruebas automáticas nunca se apuntan a la base de producción, porque limpian todos sus datos.

## Criterios de aceptación

- Todos los casos automáticos pasan y el recorrido de punta a punta termina sin errores de consola.
- Una acción prohibida responde con el código de error previsto y no modifica la base.
- Ningún caso de severidad alta queda abierto. Son de severidad alta los que afectan dinero, permisos o el estado de una operación.
- Cada requerimiento funcional tiene al menos un caso de prueba ejecutado.

## Casos de prueba

Referencias: `API` es una función de `test_flujo.py`, `E2E` es el recorrido de `flujo.mjs` y `Manual` es una verificación en el sistema publicado.

| Caso | Descripción | Resultado esperado | Requerimientos | Forma | Estado |
|---|---|---|---|---|---|
| CP-01 | Registrarse e ingresar | Se crea la cuenta y vuelve a la pantalla de origen; el correo no distingue mayúsculas | RF-01 | E2E; API `test_login_se_bloquea_temporalmente` | Automatizado |
| CP-02 | Cinco contraseñas incorrectas | Bloqueo con 429 y desbloqueo al pasar el plazo | RNF-03 | API `test_login_se_bloquea_temporalmente` | Automatizado |
| CP-03 | Datos inválidos | Contraseña demasiado larga, precio inválido e institución inexistente devuelven error del pedido | RF-01, RF-02 | API `test_validaciones_de_datos` | Automatizado |
| CP-04 | Publicar una venta con foto y colegio | La publicación aparece como publicada | RF-02 | E2E | Automatizado |
| CP-05 | Precio según el tipo | La API y la restricción de la base rechazan combinaciones inválidas | RN-01, RN-13 | API `test_validaciones_de_datos` | Automatizado |
| CP-06 | Reglas de las fotos | Rechaza fotos ajenas, formatos no permitidos, rutas manipuladas y más de 5 | RN-14 | API `test_fotos_de_publicaciones` | Automatizado |
| CP-07 | Filtros del catálogo sin sesión | Devuelve solo lo que corresponde y no muestra lo reservado | RF-03, RN-16 | API `test_catalogo_filtros_y_baja`; E2E | Automatizado |
| CP-08 | Carga por bloques | Bloques sin repetidos ni faltantes; el scroll trae el siguiente | RF-03 | API `test_catalogo_paginado`; E2E | Automatizado |
| CP-09 | Dar de baja | Solo el dueño, y nunca con una operación en curso | RF-04, RN-11 | API `test_catalogo_filtros_y_baja` | Automatizado |
| CP-10 | Reservar una venta | Operación `pendiente`, comisión del 5 % y artículo reservado | RF-05, RF-06 | API `test_venta_completa` | Automatizado |
| CP-11 | Reservar algo ya reservado | La segunda reserva se rechaza | RN-03 | API `test_venta_completa` | Automatizado |
| CP-12 | Pagar | Solo el comprador obtiene el enlace; no se paga dos veces | RF-06 | API `test_venta_completa` | Automatizado |
| CP-13 | Aviso de pago falso o repetido | Firma inválida con 401; el repetido no cambia nada | RNF-07 | API `test_webhook_rechaza_firmas_falsas_y_es_idempotente` | Automatizado |
| CP-14 | Pago de una reserva ya cancelada | Se devuelve solo y queda `reembolsado` | RF-06, RF-09 | API `test_pago_tardio_de_una_reserva_vencida_se_devuelve` | Automatizado |
| CP-15 | Compra completa en sandbox | El pago queda `retenido` en la base | RF-06 | Manual | Ejecutado el 09/11/2026 |
| CP-16 | Visibilidad del QR | Solo lo ve el comprador, y sin pago no aparece | RN-04 | API `test_venta_completa`, `test_historial_trae_datos_del_articulo`; E2E | Automatizado |
| CP-17 | Escanear | Solo el vendedor y solo con el pago retenido; el artículo queda vendido | RF-07, RN-05, RN-06 | API `test_venta_completa` | Automatizado |
| CP-18 | Escaneo con la cámara | El celular del vendedor lee el QR del comprador y confirma | RF-07, RNF-09 | Manual | Ejecutado el 09/11/2026 |
| CP-19 | Actualización de la pantalla del QR | Aparece la entrega confirmada sin recargar | RF-07 | E2E; Manual en dos celulares | E2E automatizado; manual pendiente |
| CP-20 | Datos de contacto | Solo las partes, y en las ventas recién con el pago retenido | RF-08, RN-10 | API `test_venta_completa`, `test_donacion_sin_pago` | Automatizado |
| CP-21 | Cancelar con pago retenido | Devuelve el dinero, el artículo vuelve y el QR deja de servir | RF-09, RN-08 | API `test_cancelacion_reembolsa_y_devuelve_el_articulo_al_catalogo` | Automatizado |
| CP-22 | Cancelar después de escanear | Se rechaza | RN-07 | API `test_venta_completa` | Automatizado |
| CP-23 | Devolución contra Mercado Pago | La misma llamada del backend devuelve el pago | RF-09 | Manual con dinero real (capítulo 04) | Ejecutado el 03/11/2026 |
| CP-24 | Vencimientos | Respeta los plazos de 24 horas, 7 y 4 días; solo el cron puede ejecutarlo | RF-10, RN-09 | API `test_vencimientos` | Automatizado |
| CP-25 | Donación completa | Sin pago ni comisión, con QR y contacto desde la reserva | RF-05, RN-06 | API `test_donacion_sin_pago`; E2E | Automatizado |
| CP-26 | Tope de donaciones | La cuarta se rechaza y cancelar libera un lugar; las ventas no tienen tope | RN-12 | API `test_tope_de_donaciones_pendientes` | Automatizado |
| CP-27 | Historial | Muestra los datos del artículo y oculta el QR al vendedor | RF-11 | API `test_historial_trae_datos_del_articulo` | Automatizado |
| CP-28 | Gestionar instituciones | Solo el administrador; no se borra una con publicaciones | RF-12 | API `test_catalogo_filtros_y_baja`, `test_validaciones_de_datos` | Automatizado |
| CP-29 | Colegios a pedido | Aceptar, duplicado, rechazar, elegir otro y baja mientras espera | RF-13, RN-15 | API `test_colegios_a_pedido`; E2E | Automatizado |
| CP-30 | Control de acceso | Sin sesión 401, sin permiso 403; origen ajeno bloqueado; sesión vencida lleva a ingresar | RNF-02, RNF-04, RN-16 | API `test_fotos_de_publicaciones`, `test_cors_permite_solo_el_frontend`; E2E | Automatizado |
| CP-31 | Sin desplazamiento horizontal | No hay desborde en celular, tablet ni PC | RNF-08 | E2E; capturas | Automatizado en 390 px; revisado con capturas en 820 y 1440 px |
| CP-32 | Comprar el artículo propio | Se rechaza | RN-02 | API | Pendiente |
| CP-33 | Dos reservas simultáneas | Solo una se concreta | RN-03, RNF-06 | API, con dos pedidos en paralelo | Pendiente |
| CP-34 | Error interno | La respuesta no contiene detalles técnicos | RNF-05 | API | Pendiente |
| CP-35 | Tiempo de respuesta del catálogo | Menos de 3 segundos con 100 publicaciones | RNF-10 | Medición sobre el sistema publicado | Pendiente |
| CP-36 | Prueba con usuarios | Personas ajenas al desarrollo completan una compra y una donación | OE-8 | Manual | Pendiente |

## Matriz de trazabilidad

| Requerimiento | Caso de uso | Diseño | Implementación | Pruebas |
|---|---|---|---|---|
| RF-01 | CU-01, CU-02 | Autenticación JWT | `usuario_router`, `security.py`, `Cuenta.tsx` | CP-01, CP-02, CP-03 |
| RF-02 | CU-04 | Publicación con discriminador de tipo | `publicacion_router`, `fotos.py`, `Publicar.tsx` | CP-03, CP-04, CP-05, CP-06 |
| RF-03 | CU-03 | Catálogo paginado | `publicacion_router`, `Catalogo.tsx`, `ubicacion.tsx` | CP-07, CP-08 |
| RF-04 | CU-06 | Estados de la publicación | `publicacion_router`, `MisPublicaciones.tsx` | CP-09 |
| RF-05 | CU-07 | Reserva con bloqueo de fila | `transaccion_router`, `Detalle.tsx` | CP-10, CP-11, CP-25 |
| RF-06 | CU-08 | Gateway de pagos y webhook | `pagos.py`, `pago_router`, `Transaccion.tsx` | CP-10, CP-12, CP-14, CP-15 |
| RF-07 | CU-10, CU-11 | Máquina de estados y QR | `transaccion_router`, `Transaccion.tsx`, `Escanear.tsx` | CP-17, CP-18, CP-19 |
| RF-08 | CU-09 | Control de acceso por estado | `transaccion_router`, `Transaccion.tsx` | CP-20 |
| RF-09 | CU-12 | Primero Mercado Pago, después la base | `transaccion_router`, `pagos.py` | CP-14, CP-21, CP-23 |
| RF-10 | CU-14 | Tarea programada | `transaccion_router`, `vercel.json` | CP-24 |
| RF-11 | CU-13 | Historial con datos del artículo | `transaccion_router`, `Transacciones.tsx` | CP-27 |
| RF-12 | CU-15 | Rol de administrador | `institucion_router` | CP-28 |
| RF-13 | CU-05, CU-16 | Solicitudes y estados de espera | `institucion_router`, `publicacion_router`, `Solicitudes.tsx` | CP-29 |

## Pendientes antes del cierre

Los casos CP-32 a CP-34 son pruebas automáticas chicas para agregar. CP-35 necesita definir la meta con el director. CP-36 es la validación con usuarios: conviene decidir su alcance pronto, porque depende de otras personas.
