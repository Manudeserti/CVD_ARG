# Bitácora técnica de desarrollo

**Borrador para revisar con el director.** Formato según el Instructivo, punto 7.12.4: fecha, actividad realizada, decisión adoptada, justificación, evidencia generada e impacto sobre el proyecto.

**Cómo se armó.** Las entradas hasta el 24/11/2026 se reconstruyeron el 27/11 a partir del registro de horas ([`horas.csv`](../horas.csv)), del historial de git, de las decisiones de diseño ([`docs/decisiones/`](../decisiones/)), del registro de uso de IA ([`uso-de-ia.md`](../uso-de-ia.md)) y de los mails con el director. El Instructivo (7.12.3) recomienda no reconstruir el proceso después, así que desde el 27/11 la bitácora se completa al cerrar cada sesión de trabajo. Lo que no quedó registrado en ninguna de esas fuentes figura como *a completar por el autor*.

Las horas de cada entrada son las de `horas.csv`. El detalle del uso de IA de cada sesión está en `uso-de-ia.md`.

---

## Mayo a septiembre de 2026 · 31,5 h (estimadas por el autor)

- **Actividad realizada:** relevamiento del problema, propuesta, encuesta en línea con preguntas de opción múltiple, análisis de factibilidad y redacción del protocolo, con correcciones del director.
- **Decisión adoptada:** limitar el alcance del prototipo para que entre en 200 horas; las alertas, la administración completa y la calificación quedaron como funcionalidades opcionales.
- **Justificación:** *a completar por el autor.*
- **Evidencia generada:** propuesta, resultados de la encuesta, protocolo.
- **Impacto sobre el proyecto:** define el alcance, el cronograma de 8 tareas y el plazo de entrega. El 14/09 el director pidió registrar el grado y las etapas de uso de IA, y el 20/10 el protocolo obtuvo la aprobación preliminar.

## 09/08/2026 al 22/08/2026 · 16,9 h

- **Actividad realizada:** primera versión del backend. Repositorio y estructura con FastAPI y Supabase (09 y 10/08); CRUD de instituciones, registro y login (11/08); contraseñas con bcrypt y sesión con JWT, esquemas de publicaciones y categorías (13/08); provincia en instituciones, comisión en transacciones, historial y liberación por QR (14/08); manejo de errores y flujo de donaciones (16/08); normalización de usuarios y módulo de comunicación (22/08).
- **Decisión adoptada:** las donaciones no pagan comisión; solo las ventas.
- **Justificación:** *a completar por el autor.*
- **Evidencia generada:** commits del 09/08 al 22/08 en git.
- **Impacto sobre el proyecto:** adelanta parte de las tareas 3, 4 y 5, previstas en el protocolo para octubre y noviembre.

## 22/08/2026 al 02/11/2026 · pausa

- **Actividad realizada:** ninguna sobre el Trabajo Final, salvo el cierre del protocolo en septiembre.
- **Decisión adoptada:** pausar el Trabajo Final por la dedicación a otro proyecto.
- **Justificación:** *a completar por el autor.*
- **Evidencia generada:** no hay commits entre el 22/08 y el 02/11.
- **Impacto sobre el proyecto:** el primer informe de avance, previsto para el 14/10, no se presentó. Las tareas 1 y 2 quedaron demoradas y hubo que reprogramar el Gantt.

## 02/11/2026 · 5,2 h

- **Actividad realizada:** análisis del protocolo y del código existente; elección del stack del frontend; relevamiento del marco regulatorio de la retención de fondos; corrección de huecos de seguridad de la retención; catálogo con filtros; integración con Mercado Pago (Checkout Pro, webhook, devoluciones y vencimientos); RLS en todas las tablas; tests de punta a punta; despliegue del backend en Vercel; capítulos 01 a 04 y manual técnico.
- **Decisión adoptada:**
  1. Frontend con React y Vite (decisión 001).
  2. Retención propia de los fondos, como dice el protocolo, pero solo en el entorno de pruebas de Mercado Pago (decisión 002).
  3. Backend en Vercel en lugar de Render (decisión 003).
- **Justificación:**
  1. Separación clara entre cliente y servidor, librerías de QR maduras y despliegue gratuito como sitio estático.
  2. Retener fondos de terceros con dinero real puede encuadrar como proveedor de servicios de pago (BCRA) y como sujeto obligado ante la UIF; en el entorno de pruebas no hay ese riesgo.
  3. Render gratuito duerme el servicio a los 15 minutos y no tiene tareas programadas; Vercel sí, y la tarea diaria además evita que Supabase pause la base.
- **Evidencia generada:** decisiones 001 a 003, capítulos 01 a 04, manual técnico, backend publicado.
- **Impacto sobre el proyecto:** las tareas 3 y 4 quedan casi completas en un día. Toda la infraestructura queda en dos plataformas gratuitas.

## 03/11/2026 · 1,8 h

- **Actividad realizada:** pruebas de pago en el entorno de pruebas de Mercado Pago; verificación de la devolución con dinero real; auditoría del backend (10 hallazgos) y sus correcciones; tests nuevos; reconstrucción del registro de horas e inicio del registro de uso de IA.
- **Dificultad encontrada:** Mercado Pago rechazó todas las devoluciones en el entorno de pruebas con `401 · Unauthorized use of live credentials`. Se descartaron 7 causas posibles, una por una.
- **Decisión adoptada:**
  1. Verificar la devolución con una única operación real de $100, fuera de la plataforma, entre personas conocidas y devuelta en el acto.
  2. De la auditoría: tope de 3 donaciones pendientes por usuario, plazo de 4 días para retirar una donación, bloqueo temporal del login, paginación del catálogo y restricción `CHECK` de precio en la base. Se descartó el punto 10.
  3. Modelar ventas y donaciones como una sola entidad con un campo de tipo, en lugar de dos subtipos.
- **Justificación:**
  1. Había que saber si el error era del código o del entorno de pruebas.
  2. *A completar por el autor* (cada punto se decidió en una entrevista guiada).
  3. Ventas y donaciones comparten todos los atributos salvo el precio; los subtipos solo agregarían JOINs al catálogo, que es la consulta más frecuente.
- **Evidencia generada:** capítulo 04 (tablas de las pruebas), capítulo 02, devolución aprobada por Mercado Pago (`201`, pago en estado `refunded`), `horas.csv`, `uso-de-ia.md`.
- **Impacto sobre el proyecto:** queda probado que la devolución funciona contra Mercado Pago real. Las devoluciones de la plataforma se cubren con tests automáticos que simulan a Mercado Pago.

## 09/11/2026 · 5,8 h

- **Actividad realizada:** lectura de los documentos de la cátedra; bocetos de interfaz; fotos de las publicaciones; colegios a pedido; frontend completo en React; diseño para PC y tablet; provincias y localidades oficiales; buscador de colegios; logo; despliegue del frontend; compra en el entorno de pruebas y escaneo del QR entre dos celulares reales, con la pantalla del QR actualizándose sola (CP-19); borradores de los informes de avance, casos de uso, diseño y plan de pruebas.
- **Dificultad encontrada:** con un mail real o con la sesión de una cuenta real, Mercado Pago rechaza el pago con "una de las partes es de prueba". El pago funcionó como invitado, con la tarjeta de prueba aprobada.
- **Decisión adoptada:**
  1. Los colegios se agregan a pedido: primero se elige la ciudad y después el colegio; si no está, la publicación queda pendiente hasta que se acepte la solicitud desde el panel (RN-15).
  2. TypeScript en el frontend y `@yudiel/react-qr-scanner` en lugar de `html5-qrcode` (actualización de la decisión 001).
  3. Administración mínima: solo la pantalla de solicitudes de colegios.
  4. Localidades de Georef, el servicio oficial de normalización geográfica.
- **Justificación:**
  1. *A completar por el autor.*
  2. Los tipos evitan errores con los estados de una operación; la última versión de `html5-qrcode` es de 2023.
  3. El panel completo es opcional en el protocolo y la API ya cubre la gestión de instituciones.
  4. *A completar por el autor.*
- **Evidencia generada:** frontend publicado, capítulo 05, `frontend/e2e/flujo.mjs` (24 pasos), capturas en tres anchos, borradores de los capítulos 00, 01, 06, 07 y 08.
- **Impacto sobre el proyecto:** la tarea 6 y la tarea 5 quedan terminadas. El sistema completo queda publicado y probado de punta a punta.

## 16/11/2026 · 3,4 h

- **Actividad realizada:** se rehicieron los diagramas UML con el libro de la cátedra (Larman): casos de uso, modelo del dominio, secuencia de pagar y cancelar, estados de la operación y de la publicación, paquetes, despliegue, modelo de datos y navegación. Camino crítico en el Gantt.
- **Decisión adoptada:** seguir la notación de Larman en todos los diagramas, uno por vez, solo los que pide la tesis.
- **Justificación:** es la bibliografía de la materia y la forma en que se enseñaron los diagramas en la facultad.
- **Evidencia generada:** `docs/memoria/diagramas/` (10 diagramas y sus generadores), capítulos 06 y 07.
- **Impacto sobre el proyecto:** las tareas 1 y 2 quedan en borrador completo, a revisar con el director.

## 17/11/2026 · 1,0 h

- **Actividad realizada:** informes de avance y Gantt con fechas nuevas; mail al director con los dos informes.
- **Decisión adoptada:** en el objetivo específico 5 y en el alcance, "pasarela de pago (Mercado Pago)" en lugar de "billetera virtual". El marco teórico se marca como cumplido parcialmente.
- **Justificación:** describe con más precisión lo que hace el sistema, que cobra a través de Mercado Pago. El marco teórico todavía no tiene fuentes leídas ni citas.
- **Evidencia generada:** `docs/informes/` (Gantt y dos checklists .docx), capítulo 00.
- **Impacto sobre el proyecto:** los informes quedan listos para la revisión del director.

## 18/11/2026 · 1,0 h

- **Actividad realizada:** búsqueda y verificación de 21 fuentes para el marco teórico y de las plataformas del estado del arte; consulta a la cátedra sobre presentar los dos informes juntos.
- **Decisión adoptada:** la lectura de las fuentes y la elección de qué citar quedan a cargo del autor.
- **Justificación:** no se cita nada que no se haya leído.
- **Evidencia generada:** `docs/fuentes/fuentes-marco-teorico.html`.
- **Impacto sobre el proyecto:** aparece el diferencial frente a plataformas parecidas: retención del pago, QR en la entrega presencial y organización por colegio. El director avisa que revisa los informes la semana siguiente.

## 23/11/2026 y 24/11/2026 · sin horas registradas

- **Actividad realizada:** respuesta del director y acuerdo de reunión para la semana del 30/11, por la mañana.
- **Decisión adoptada:** pedidos del director: presentar el último Gantt con la justificación del atraso (consultándolo antes con la cátedra), medir el retrabajo y la tasa de errores introducidos por la IA, compartir la documentación del proyecto (EDT y bitácora) y mostrar el avance en una reunión.
- **Justificación:** según el director, la IA aceleró mucho el desarrollo y dejó holgura para sumar funcionalidades, pero la estimación de horas no fue acertada.
- **Evidencia generada:** mails del 23 y 24/11.
- **Impacto sobre el proyecto:** se arman la EDT y esta bitácora, y hay que sumar indicadores de retrabajo de IA al registro.

## 27/11/2026 · *horas a completar*

- **Actividad realizada:** revisión de los documentos de la cátedra sobre la EDT y la bitácora; borradores de la EDT y de esta bitácora.
- **Decisión adoptada:** la EDT toma como primer nivel las 8 tareas del protocolo. La bitácora sigue los campos del Instructivo 7.12.4.
- **Justificación:** la cátedra no pide un formato para la EDT; mantener las 8 tareas permite compararla con el Gantt y con las horas registradas.
- **Evidencia generada:** `docs/gestion/edt.md`, `edt.svg`, `edt.png`, `bitacora.md`.
- **Impacto sobre el proyecto:** queda la documentación que pidió el director para la reunión.
