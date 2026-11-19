# Registro de uso de inteligencia artificial

El director pidió registrar en qué grado y en qué etapas se usa IA, para incluirlo en el informe final (mail del 14/09/2026). Este registro se completa al cerrar cada sesión de trabajo, junto con [`horas.csv`](horas.csv).

## Grados

| Grado | Significado |
|---|---|
| Bajo | Consultas puntuales: dudas, explicaciones, documentación. El autor escribe todo. |
| Intermedio | La IA propone fragmentos o borradores; el autor los integra y modifica. |
| Alto | La IA escribe el código o el texto; el autor define qué se hace, cuestiona cada propuesta, aprueba los cambios y verifica el resultado. |

## Lo declarado en el protocolo

En el protocolo se declaró un uso de grado **intermedio**, principalmente en la integración con Mercado Pago y en el testing, presentado como fortaleza para compensar la falta de experiencia con plataformas de pago.

En la práctica, desde noviembre de 2026 el uso es de grado **alto** en todo el código: la IA escribe la implementación bajo el control del autor. La diferencia queda registrada acá para explicarla en el informe.

## Registro

| Fecha | Actividad | Herramienta | Qué hizo la IA | Qué hizo el autor | Grado |
|---|---|---|---|---|---|
| 05–09/2026 | 1 Requerimientos | *A completar por el autor* | *A completar* (el director observó en junio un uso evidente de IA en la redacción de la propuesta) | Idea, investigación, encuesta y su difusión, correcciones con el director | *A completar* |
| 08/2026 | 3 Backend y API | Gemini | *A completar*: asistencia en el backend inicial (FastAPI, autenticación, publicaciones, transacciones, liberación por QR) | *A completar* | *A completar* |
| 02/11/2026 | 1, 2, 3, 4, 7, 8 | Claude Code (Claude Opus) | Análisis del código y del protocolo; plan de desarrollo; comparativa de stacks; relevamiento regulatorio; correcciones de seguridad del escrow; catálogo con filtros; integración con Mercado Pago (pagos, webhook, devoluciones, vencimientos); tests; configuración del despliegue; borradores de los capítulos 01 a 04 y de las decisiones 001 a 003 | Eligió el stack y el enfoque regulatorio; decidió mantener la retención propia del protocolo; creó y configuró Supabase, Vercel y Mercado Pago; aprobó cada commit y cada merge | Alto |
| 03/11/2026 | 4, 7, 8 | Claude Code (Claude Opus) | Diagnóstico de las devoluciones en el sandbox de Mercado Pago; script de la prueba con dinero real; búsqueda en la documentación oficial con el MCP de Mercado Pago | Hizo los pagos de prueba; consiguió quien pagara la prueba real; decidió hacer la verificación con dinero real | Alto |
| 03/11/2026 | 3, 7, 8 | Claude Code (Claude Opus) | Auditoría del backend (informe con 10 hallazgos y propuestas); implementación de las correcciones aprobadas; tests; migración de Supabase; actualización de los capítulos 01 a 03 | Decidió cada punto en una entrevista guiada: tope de 3 donaciones, plazo de 4 días, bloqueo temporal del login, paginación para scroll infinito, `CHECK` de precio en la base; descartó el punto 10; propuso modelar ventas y donaciones como subtipos (se documentó por qué se eligió otra opción) | Alto |
| 03/11/2026 | 1, 8 | Claude Code (Claude Opus) | Reconstrucción de las horas a partir de git, de los registros de las sesiones y de los mails con el director | Estimó sus propias horas por etapa (31,5 h para requerimientos) y corrigió las de la sesión | Intermedio |
| 09/11/2026 | 2, 3, 6, 7, 8 | Claude Code (Claude Opus) | Lectura de los documentos de la cátedra; plan del sprint; bocetos de interfaz; subida de fotos con Supabase Storage; colegios a pedido; CORS; historial con datos del artículo; frontend en React completo; tests y prueba de punta a punta en Chrome; borradores de la documentación del frontend | Definió la regla de colegios a pedido (primero ciudad y después colegio, publicación pendiente hasta aceptar la solicitud, qué pasa si se rechaza); confirmó el panel mínimo de solicitudes; decidió no mergear a main hasta revisar la rama | Alto |
| 16/11/2026 | 1, 2, 8 | Claude Code (Claude Opus) | Lectura del índice y de los capítulos del libro de la cátedra (Larman) para cada diagrama; comparación con los diagramas existentes; dibujo de los diagramas en SVG; ajuste de los textos de los capítulos 01, 02, 03, 05, 06 y 07; camino crítico en el Gantt | Aportó el libro y el método (un diagrama por vez, solo los que pide la tesis); decidió cada cambio: nivel de los casos de uso, «include», generalización Venta/Donación, Provincia y Localidad como clases conceptuales, módulos reales en la secuencia, notas solo para los efectos en la base, rombos del modelo de datos, navegación como diagrama de estados; cuestionó la notación (corchetes, notas, componentes en la secuencia); dejó el Gantt para después de hablar con el director | Intermedio |
| 17/11/2026 | 8 | Claude Code (Claude Opus) | Revisión del mensaje al director según el avance; actualización de fechas y textos de los checklists; regeneración del Gantt y de los .docx; lectura del Instructivo sobre marco teórico y estado del arte; propuesta de temas | Decidió los cambios al mensaje; pidió que los textos reflejen el respaldo real de las decisiones; pasó el marco teórico a cumplido parcialmente; dejó la búsqueda de fuentes como próximo paso, con la lectura a su cargo; hizo corregir varias veces los textos propuestos | Intermedio |
| 18/11/2026 | 8 | Claude Code (Claude Opus) | Repaso de las pautas de los informes de avance sobre entregas atrasadas; borradores de los mails al director y a la cátedra; búsqueda y verificación en la web de 21 fuentes para el marco teórico y de las plataformas del estado del arte, con qué leer de cada una | Decidió acortar los mails y a quién dirigirlos; pidió consultar a la cátedra por presentar los dos informes juntos; queda a su cargo leer las fuentes y decidir cuáles citar | Intermedio |

## Forma de trabajo acordada desde noviembre de 2026

- La IA escribe el código; el autor controla, cuestiona y aprueba cada cambio antes de que se aplique.
- Las auditorías son solo informes con propuestas: no se modifica nada sin la aprobación del autor.
- Los textos de la memoria y de los manuales que redacta la IA son borradores: el autor los revisa y los reescribe con su voz.
