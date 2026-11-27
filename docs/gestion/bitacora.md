# Bitácora técnica de desarrollo


## Mayo a septiembre de 2026 · 31,5 h 

- **Actividad realizada:** relevamiento del problema, propuesta, encuesta en línea con preguntas de opción múltiple, análisis de factibilidad y redacción del protocolo, con correcciones del director.
- **Decisión adoptada:** limitar el alcance del prototipo para que entre en 200 horas; las alertas, la administración completa y la calificación quedaron como funcionalidades opcionales.
- **Justificación:** propuesta de la cátedra.
- **Evidencia generada:** propuesta, resultados de la encuesta, protocolo.
- **Impacto sobre el proyecto:** define el alcance, el cronograma de 8 tareas y el plazo de entrega.

## 09/08/2026 y 10/08/2026 · 3,9 h

- **Actividad realizada:** creación del repositorio; estructura del backend con FastAPI y conexión a Supabase; validación de los datos de entrada de las instituciones.
- **Decisión adoptada:** backend en Python con FastAPI y base de datos PostgreSQL en Supabase. Validar los datos de entrada antes de que lleguen a la base de datos.
- **Justificación:** Supabase tiene un plan gratuito. Usé Python en varios proyectos anteriormente. No se puede confiar en datos que carga un tercero ajeno al sistema.
- **Evidencia generada:** commits del 09 y 10/08 en git.
- **Impacto sobre el proyecto:** empieza la tarea 3, que el protocolo preveía para más adelante.

## 11/08/2026 · 3,9 h

- **Actividad realizada:** alta, baja y modificación de instituciones; registro y login de usuarios.
- **Decisión adoptada:**  Contraseñas guardadas con bcrypt, nunca en texto plano. Se eligió el borrado definitivo en la baja de instituciones.
- **Justificación:** Si alguien accede a la base, no puede leer las contraseñas. En cuanto al borrado definitivo, por simplicidad; en noviembre se sumó el aviso cuando el colegio tiene publicaciones asociadas.
- **Evidencia generada:** commits del 11/08 en git.
- **Impacto sobre el proyecto:** avanza la tarea 3.

## 13/08/2026 · 3,0 h

- **Actividad realizada:** autenticación de usuarios; esquemas de publicaciones y categorías de artículos.
- **Decisión adoptada:** sesión con token JWT, venta y donación como una sola publicación.
- **Justificación:** el servidor no tiene que guardar las sesiones: cada pedido trae el token y alcanza con verificar la firma. Las ventas y las donaciones tienen los mismos datos salvo el precio, que en una donación es 0. Con una sola tabla y un campo tipo, el catálogo muestra las dos en una única consulta, sin unir tablas.
- **Evidencia generada:** commits del 13/08 en git.
- **Impacto sobre el proyecto:** avanzan las tareas 2 y 3.

## 14/08/2026 · 3,0 h

- **Actividad realizada:** catálogo público; comisión en las transacciones; historial de transacciones y liberación de fondos por QR.
- **Decisión adoptada:**
  1. El vendedor se toma del token, no de los datos que manda el cliente.
  2. Cada usuario puede ver sus transacciones, como comprador y como vendedor.
  3. No se puede comprar un artículo propio ni uno que no esté disponible.
  4. Solo el vendedor puede escanear el QR, y solo si el pago está pendiente.
- **Justificación:** 
  1. Así nadie puede publicar a nombre de otro.
  2. Cada usuario tiene registro de lo que hizo.
  3. Evita que un artículo se venda dos veces o que alguien se compre a sí mismo.
  4. El dinero se libera solo cuando el comprador recibe el artículo en persona.
- **Evidencia generada:** commits del 14/08 en git.
- **Impacto sobre el proyecto:** se adelanta parte de las tareas 4 y 5.

## 16/08/2026 · 1,6 h

- **Actividad realizada:** publicación de donaciones, sin comisión, como define el protocolo; validación de precios según el tipo de publicación; manejo de errores unificado.
- **Decisión adoptada:**
  1. Una venta tiene que tener precio mayor a 0 y una donación no puede tener precio.
  2. Los errores esperados le llegan al cliente con su mensaje y su código; los inesperados devuelven un error 500.
  3. La conexión a la base se cierra siempre, aunque falle la consulta.
- **Justificación:** 
  1. Evita publicaciones contradictorias, como una venta gratis o una donación con precio, y el error se avisa antes de tocar la base.
  2. El frontend puede distinguir un error del usuario, para mostrarle qué corregir, de una falla del sistema.
  3. Las conexiones que quedan abiertas se acumulan y pueden agotar las que permite la base.
- **Evidencia generada:** commits del 16/08 en git.
- **Impacto sobre el proyecto:** avanza la tarea 4.

## 22/08/2026 · 1,5 h

- **Actividad realizada:** Normalización de usuarios y módulo de comunicación
- **Decisión adoptada:** 
  1. Separar "nombre completo" en nombre y apellido.
  2. Se comparten el nombre, el apellido y el teléfono de la otra parte, pero no el mail.
- **Justificación:** 
  1. Con nombre y apellido separados se puede ordenar y buscar por apellido, y mostrar solo el nombre donde no hace falta el completo. Además, cada campo guarda un único dato.
  2. El teléfono alcanza para coordinar la entrega en persona. El mail es el usuario con el que se inicia sesión; compartirlo le da a un desconocido la mitad de los datos para intentar entrar a la cuenta.
- **Evidencia generada:** commits del 22/08 en git.
- **Impacto sobre el proyecto:** avanza la tarea 3. Es lo último antes de la pausa.

## 22/08/2026 al 31/10/2026 · pausa

- **Actividad realizada:** ninguna sobre el trabajo final, salvo el cierre del protocolo en septiembre.
- **Decisión adoptada:** pausar el trabajo final por la dedicación a otro proyecto.
- **Justificación:** Comencé a desarrollar otro proyecto a la par, pero me demandó más tiempo del esperado. Por lo que decidí pausar el trabajo final.
- **Evidencia generada:** no hay commits entre el 22/08 y el 02/11.
- **Impacto sobre el proyecto:** el primer informe de avance, previsto para el 14/10, no se presentó. Las tareas 1 y 2 quedaron demoradas y hubo que reprogramar el Gantt.

## 01/11/2026 al 02/11/2026 · 8,2 h

- **Actividad realizada:** análisis del código existente (01/11, sin commits); análisis del protocolo; elección del stack del frontend; relevamiento del marco regulatorio de la retención de fondos; corrección de huecos de seguridad de la retención; catálogo con filtros; integración con Mercado Pago (Checkout Pro, webhook, devoluciones y vencimientos); base nueva en Supabase con el esquema versionado; RLS en todas las tablas; tests de punta a punta; despliegue del backend en Vercel; capítulos 01 a 04 y manual técnico.

- **Dificultad encontrada:** la base de Supabase de agosto quedó congelada por inactividad durante la pausa.

- **Decisión adoptada:**
  1. Frontend con React y Vite (decisión 001).
  2. Retención propia de los fondos, como dice el protocolo, pero solo en el entorno de pruebas de Mercado Pago (decisión 002).
  3. Backend en Vercel en lugar de Render (decisión 003).
  4. Crear una base nueva a partir de `schema.sql` y versionar el esquema en git.
  5. El código QR solo se le entrega al comprador.
  6. Impedir que dos personas compren el mismo artículo al mismo tiempo.
  7. Compartir los datos de contacto recién con el pago retenido, y sumar el mail (se revierte lo decidido el 22/08).
  8. Cualquiera de las partes puede cancelar mientras no haya escaneo. La operación vence a los 7 días sin escaneo, y una venta reservada sin pagar se libera a las 24 horas.
  9. Baja lógica para las publicaciones.
  10. No dar por cierto un aviso de Mercado Pago sin verificar su firma y consultar el pago a su API; al cancelar, pedir el reembolso antes de cambiar la base.
  11. RLS en todas las tablas.

- **Justificación:**
  1. Separación clara entre cliente y servidor, librerías de QR confiables y despliegue gratuito.
  2. Retener fondos de terceros con dinero real puede tomarse como proveedor de servicios de pago (BCRA) y como sujeto obligado ante la UIF; en el entorno de pruebas no hay ese riesgo.
  3. Render gratuito duerme el servicio a los 15 minutos y no tiene tareas programadas; Vercel sí, y la tarea diaria además evita que Supabase pause la base.
  4. Con el esquema en git, la base se recrea en minutos si se pierde; la tarea diaria de la decisión 3 evita que vuelva a congelarse.
  5. El QR prueba que el comprador recibió el artículo; si lo tuviera el vendedor, podría liberarse el dinero sin entregar nada.
  6. Sin el bloqueo, dos compras simultáneas podían reservar el mismo artículo.
  7. Los datos personales se comparten solo cuando hay una compra en firme. El teléfono es opcional en el registro; sin el mail, una operación con alguien que no cargó teléfono quedaba sin forma de coordinar la entrega.
  8. Si el encuentro no se concreta, nadie queda atado a la operación. Siete días alcanzan para coordinar un encuentro, incluido un fin de semana, sin dejar el dinero retenido indefinidamente; 24 horas evitan que una reserva sin pago bloquee el artículo para los demás.
  9. Una publicación puede tener operaciones y pagos asociados; borrarla dejaría el historial sin el artículo al que se refiere.
  10. Cualquiera puede mandar un aviso falso a la dirección del webhook. Si Mercado Pago rechaza un reembolso, la operación queda como estaba y no se registra como devuelto un dinero que no volvió.
  11. Supabase publica las tablas en su API con una clave que es pública; sin RLS, cualquiera podía leer o modificar la base salteándose el backend.

- **Evidencia generada:** commits del 02/11 en git, decisiones 001 a 003, `schema.sql`, `tests/test_flujo.py`, capítulos 01 a 04, manual técnico, backend publicado.
- **Impacto sobre el proyecto:** las tareas 3 y 4 quedan casi completas. Toda la infraestructura queda en dos plataformas gratuitas.


## 03/11/2026 · 3,2 h

- **Actividad realizada:** pruebas de pago en el entorno de pruebas de Mercado Pago; verificación de la devolución con dinero real; auditoría del backend (10 hallazgos) y sus correcciones; tests nuevos; reconstrucción del registro de horas.
- **Dificultad encontrada:** Mercado Pago rechazó todas las devoluciones en el entorno de pruebas con `401 · Unauthorized use of live credentials`. Se descartaron 7 causas posibles, una por una, y llevó bastante tiempo concluir que el problema era del entorno de pruebas y no del código, y pasar a verificarlo con dinero real.

- **Decisión adoptada:**
  1. Verificar la devolución con una única operación real de $100, fuera de la plataforma, entre personas conocidas y devuelta en el acto.
  2. Tope de 3 donaciones pendientes por usuario.
  3. Plazo de 4 días para retirar una donación, en lugar de los 7 de las ventas.
  4. Bloqueo de la cuenta por 15 minutos después de 5 intentos de login fallidos.
  5. Catálogo paginado de a 20 publicaciones.
  6. La regla de precio según el tipo de publicación se controla también en la base.
  7. Los errores internos le muestran al usuario un mensaje genérico; el detalle queda en los registros del servidor.
  8. El mail se guarda en minúsculas.
  9. Se evaluó modelar Publicación como una interfaz de la que se desprendan Venta y Donación; se mantuvo una sola publicación con el atributo `tipo`.
- **Justificación:**
  1. Había que saber si el error era del código o del entorno de pruebas.
  2. Evita que una persona reserve muchas donaciones sin retirarlas y deje a otros sin acceso a ellas.
  3. En una donación no hay dinero retenido, así que no hace falta tanto margen; el artículo vuelve antes a estar disponible para otro.
  4. Frena los intentos de adivinar una contraseña probando muchas seguidas.
  5. El catálogo no trae todas las publicaciones de una vez: carga más a medida que el usuario baja.
  6. La regla se cumple aunque alguien escriba en la base sin pasar por la API.
  7. El mensaje técnico mostraba detalles internos de la base a cualquiera.
  8. Evita cuentas duplicadas y logins fallidos por escribir el mail con mayúsculas distintas.
  9. Ventas y donaciones comparten todos los atributos salvo el precio; separarlas solo agregaría uniones de tablas al catálogo, que es la consulta más frecuente. En el modelo del dominio se representan como subtipos de Publicación.
- **Evidencia generada:** capítulo 04 (tablas de las pruebas), capítulo 02, devolución aprobada por Mercado Pago (`201`, pago en estado `refunded`), `horas.csv`, `uso-de-ia.md`.
- **Impacto sobre el proyecto:** queda probado que la devolución funciona contra Mercado Pago real. Las devoluciones de la plataforma se cubren con tests automáticos que simulan a Mercado Pago.

## 09/11/2026 · 8,8 h

- **Actividad realizada:** lectura de los documentos de la cátedra; bocetos de interfaz; fotos de las publicaciones; colegios a pedido; frontend completo en React; diseño para PC y tablet; provincias y localidades oficiales; buscador de colegios; logo; despliegue del frontend; compra en el entorno de pruebas y escaneo del QR entre dos celulares reales, con la pantalla del QR actualizándose sola (CP-19); borradores de los informes de avance, casos de uso, diseño y plan de pruebas.
- **Dificultad encontrada:** con un mail real o con la sesión de una cuenta real, Mercado Pago rechaza el pago con "una de las partes es de prueba". El pago funcionó como invitado, con la tarjeta de prueba aprobada.
- **Decisión adoptada:**
  1. Los colegios se agregan a pedido: primero se elige la ciudad y después el colegio; si no está, la publicación queda pendiente hasta que se acepte la solicitud desde el panel (RN-15).
  2. TypeScript en el frontend y `@yudiel/react-qr-scanner` en lugar de `html5-qrcode` (actualización de la decisión 001).
  3. Administración mínima: solo la pantalla de solicitudes de colegios.
  4. Localidades de Georef, el servicio oficial de normalización geográfica.
  5. Hasta 5 fotos por publicación, en JPG, PNG o WebP y de hasta 5 MB cada una, guardadas en Supabase Storage (RN-14).
  6. La pantalla del QR se actualiza consultando cada 5 segundos, en lugar de mantener una conexión en tiempo real.
- **Justificación:**
  1. No se pueden cargar de antemano todos los colegios del país: se agregan a medida que los usuarios los necesitan, y el administrador revisa cada pedido para que no haya duplicados ni colegios inexistentes.
  2. Los tipos evitan errores con los estados de una operación; la última versión de `html5-qrcode` es de 2023.
  3. El panel completo es opcional en el protocolo y la API ya cubre la gestión de instituciones.
  4. Nombres oficiales y uniformes de provincias y localidades. Si cada usuario escribiera su ciudad, la misma aparecería de varias formas ("Mar del Plata", "MdP") y los filtros del catálogo no funcionarían.
  5. El límite cuida el espacio del plan gratuito de Supabase, y esos formatos los muestra cualquier navegador.
  6. El backend corre en Vercel, que no mantiene conexiones abiertas. Una consulta cada 5 segundos es simple y alcanza, porque el comprador espera unos segundos frente al vendedor.
- **Evidencia generada:** commits del 09/11 en git, frontend publicado, logo, capítulo 05, `frontend/e2e/flujo.mjs` (24 pasos), capturas en tres anchos, borradores de los informes de avance y de los capítulos 00, 01, 06, 07 y 08.
- **Impacto sobre el proyecto:** las tareas 5 y 6 quedan terminadas. El sistema completo queda publicado y probado de punta a punta.

## 16/11/2026 · 3,4 h

- **Actividad realizada:** se rehicieron los diagramas UML con el libro de la cátedra (Larman): casos de uso, modelo del dominio, secuencia de pagar y cancelar, estados de la operación y de la publicación, paquetes, despliegue, modelo de datos y navegación. Camino crítico en el Gantt.
- **Decisión adoptada:**
  1. Seguir la notación de Larman en todos los diagramas, uno por vez, solo los que pide la tesis.
  2. Casos de uso en formato completo; los pasos que se repiten en varios casos se separan en casos de nivel subfunción, relacionados con «include».
  3. En el modelo del dominio, Venta y Donación se representan como subtipos de Publicación.
  4. Provincia y Localidad como clases conceptuales, no como atributos.
  5. La navegación entre pantallas se representa con un diagrama de estados.
  6. No incluir un diagrama de clases de diseño (provisorio, a confirmar con el director).
- **Justificación:**
  1. Es la bibliografía de la materia y la forma en que se enseñaron los diagramas en la facultad.
  2. Un paso común se escribe una sola vez y los demás casos lo referencian.
  3. En el dominio son conceptos distintos, con reglas propias (comisión, plazos, tope de donaciones). En la base se guardan en una sola tabla (ver 03/11): el modelo del dominio representa conceptos, no tablas.
  4. Según Larman, si algo no es un número o un texto simple en el mundo real, es una clase conceptual. Provincias y localidades tienen identidad propia y vienen de un catálogo oficial (Georef).
  5. Larman propone los diagramas de estados para modelar la navegación de la interfaz: cada pantalla es un estado y cada acción del usuario, una transición.
  6. El backend sigue el estilo de guion de transacción y el frontend usa componentes funcionales de React. Casi no hay clases propias con métodos que dibujar.
- **Evidencia generada:** commits del 16/11 en git, `docs/memoria/diagramas/` (10 diagramas y sus generadores), capítulos 06 y 07.
- **Impacto sobre el proyecto:** diagramas más completos y alineados a la nomenclatura estudiada.


## 17/11/2026 · 1,0 h

- **Actividad realizada:** informes de avance y Gantt con fechas nuevas; revisión de los checklists; mail al director con los dos informes.
- **Decisión adoptada:**
  1. En el objetivo específico 5 y en el alcance, "pasarela de pago (Mercado Pago)" en lugar de "billetera virtual".
  2. El marco teórico se marca como cumplido parcialmente.
  3. Nuevas fechas en el Gantt: las tareas 1 y 2 cierran con las correcciones del director, y el marco teórico va del 18/11 al 30/11.
  4. Proponer al director presentar el primer informe junto con el segundo, con un solo Gantt.
  5. Consultar al director si se pueden sumar las funcionalidades opcionales del protocolo sin cambiar los objetivos ni la fecha de entrega, y esperar su respuesta antes de empezarlas.
- **Justificación:**
  1. Describe con mayor precisión lo que hace el sistema, que cobra a través de Mercado Pago.
  2. El marco teórico todavía no tiene fuentes leídas ni citas.
  3. La pausa dejó desactualizado el cronograma original, y las tareas 1 y 2 dependen de la revisión del director.
  4. El primer informe no se presentó el 14/10. Presentar los dos con el estado real evita entregar un documento ya desactualizado.
  5. El uso de IA bajó los tiempos del desarrollo y dejó horas disponibles, pero sumar alcance sin consultar podía obligar a modificar el protocolo.
- **Evidencia generada:** commits del 17/11 en git, `docs/informes/` (Gantt y dos checklists .docx), capítulo 00, mail del 17/11 al director.
- **Impacto sobre el proyecto:** los informes quedan listos para la revisión del director.

## 18/11/2026 · 2,5 h

- **Actividad realizada:** búsqueda y verificación de 21 fuentes para el marco teórico y de las plataformas del estado del arte; consulta a la cátedra sobre presentar los dos informes juntos.
- **Decisión adoptada:**
  1. Consultar a la cátedra si se pueden presentar los dos informes juntos, después de la revisión del director, con un solo Gantt.
  2. Además de libros y artículos, usar documentación técnica oficial y normas, y vincular cada fuente con una parte del diseño, la implementación o las pruebas.
  3. La lectura de las fuentes y la elección de qué citar quedan a cargo del autor.
- **Justificación:**
  1. El director no llegaba a revisar los informes antes del 19/11; convenía consultar antes de presentarlos sin su revisión.
  2. El Instructivo (7.4) acepta documentación oficial y normas, y pide que cada concepto del marco teórico se relacione con el trabajo.
  3. No se cita nada que no se haya leído.
- **Evidencia generada:** `docs/fuentes/fuentes-marco-teorico.html`, mail a la cátedra del 18/11.
- **Impacto sobre el proyecto:** aparece el diferencial frente a plataformas parecidas: retención del pago, QR en la entrega presencial y organización por colegio. 



## 27/11/2026 · 3,2 h

- **Actividad realizada:** revisión de la EDT y de esta bitácora.
- **Decisión adoptada:** reestructuración de la EDT y pasada en limpio de la bitácora 
- **Justificación:** la cátedra no pide un formato para la EDT; la bitácora era un borrador con notas informales de las decisiones tomadas con sus justificaciones.
- **Evidencia generada:** `docs/gestion/edt.md`, `edt.svg`, `edt.png`, `bitacora.md`.
- **Impacto sobre el proyecto:** mejor documentación del proyecto.
