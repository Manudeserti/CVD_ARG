# 00 · Introducción, objetivos y metodología

> Borrador para reescribir con la voz del autor. Sale del protocolo (presentado el 09/09/2026, con correcciones del 14/09) y del registro del proyecto. Los objetivos específicos son una propuesta: el protocolo solo define el objetivo general, y hay que confirmarlos con el director.

## Introducción

### Contexto

Cada año las familias compran uniformes, guardapolvos, libros y útiles que los chicos dejan de usar en poco tiempo. Parte de esos artículos vuelve a circular de segunda mano, pero de manera informal: por el boca a boca, en grupos de WhatsApp, en Facebook Marketplace o en ferias de donación.

### Motivación

Para medir el problema se hizo una encuesta dirigida a padres y a mayores con familiares en edad escolar, que alcanzó 381 respuestas. El 85,5 % ya compra, vende o dona artículos escolares de segunda mano. Lo hace por el boca a boca (66,1 %), por grupos de WhatsApp (50,6 %) o por Marketplace (43,2 %). El 89,1 % considera muy importante poder filtrar lo que busca y el 91,6 % considera relevante un módulo para donaciones.

### Problema a resolver

La informalidad tiene costos concretos. El 44,8 % de los encuestados sufrió cancelaciones del encuentro y el 38,4 % pierde tiempo leyendo mensajes o publicaciones que no tienen que ver con lo que busca. Quien paga antes de recibir el artículo no tiene ninguna garantía, y quien entrega antes de cobrar tampoco. Las donaciones se concentran en ferias masivas o quedan limitadas al círculo cercano, sin posibilidad de elegir talle. No se encontró en Argentina una plataforma que reúna compra, venta y donación escolar con seguridad en la operación.

### Alcance y delimitaciones

El trabajo desarrolla un prototipo académico de plataforma web responsiva, con alcance geográfico nacional, que incluye:

- catálogo con filtros por provincia, ciudad, institución y tipo de artículo;
- publicaciones de venta y de donación;
- retención del pago mediante una billetera virtual hasta confirmar la entrega, con una comisión porcentual en las ventas;
- validación presencial de la entrega con un código QR, también en las donaciones;
- intercambio de los datos de contacto entre las partes de cada operación.

El protocolo marca como opcionales las instituciones por demanda, las alertas automáticas, el módulo de administración y la calificación de usuarios. De esas funcionalidades se implementó el alta de colegios a pedido, con una pantalla mínima para resolver las solicitudes.

Quedan fuera del alcance el envío por correo, porque el modelo se basa en el encuentro presencial, y los pagos fuera de las billeteras virtuales. Por tratarse de un prototipo, los pagos funcionan en el entorno de pruebas de Mercado Pago. El capítulo 04 analiza qué haría falta para operar con dinero real.

## Objetivos

### Objetivo general

Desarrollar una plataforma que centralice, optimice y asegure la compra, venta y donación de artículos y uniformes escolares de segunda mano, con el fin de fomentar la economía circular escolar mediante un sistema de retención de pagos y validación presencial orientado a reducir los riesgos en las transacciones.

### Objetivos específicos (propuesta)

| Código | Objetivo específico | Cómo se verifica |
|---|---|---|
| OE-1 | Relevar la necesidad de los usuarios y especificar los requerimientos del sistema | Encuesta analizada; requerimientos y casos de uso aprobados por el director |
| OE-2 | Diseñar la arquitectura, el modelo de datos y la interfaz de la plataforma | Diseño documentado y coherente con los requerimientos |
| OE-3 | Implementar un catálogo que permita encontrar artículos por ubicación, institución y tipo | Casos de prueba del catálogo aprobados |
| OE-4 | Implementar la publicación de artículos en venta y en donación | Casos de prueba de publicaciones aprobados |
| OE-5 | Integrar una pasarela de pago (Mercado Pago) que permita retener los fondos en la plataforma hasta la entrega y devolverlos si la operación no se concreta | Compra y devolución verificadas contra Mercado Pago |
| OE-6 | Implementar la validación presencial de la entrega mediante un código QR | Escaneo verificado con celulares reales |
| OE-7 | Facilitar el contacto entre las partes de cada operación | Casos de prueba de contacto aprobados |
| OE-8 | Desplegar la plataforma y validarla frente a los requerimientos | Plan de pruebas ejecutado sobre el sistema publicado |

## Metodología

### Relevamiento

Se partió de una propuesta revisada con el director y de una encuesta en línea con preguntas de opción múltiple. Sus resultados sustentaron el análisis de factibilidad y la definición del alcance del protocolo.

### Desarrollo

El proyecto se desarrolla de manera individual con un enfoque ágil e incremental, en iteraciones cortas que terminan con un producto ejecutable y con su parte de documentación:

| Iteración | Contenido |
|---|---|
| Base (agosto de 2026) | Backend inicial: autenticación, publicaciones, transacciones y liberación por QR |
| Sprint A | Seguridad de la retención de fondos, catálogo con filtros, modelo de datos y requerimientos |
| Sprint B | Integración con Mercado Pago y despliegue del backend |
| Sprint C | Frontend responsive, fotos, colegios a pedido y despliegue del frontend |
| Sprint D | Plan de pruebas, correcciones, manuales y memoria |

El trabajo se pausó entre el 22/08 y el 02/11/2026 por la dedicación del autor a otro proyecto. El Gantt actualizado muestra el efecto de esa pausa.

Cada decisión de diseño importante se registra en `docs/decisiones/` con sus alternativas y su justificación. El código se versiona con Git, se trabaja siempre en ramas y cada iteración se integra a la rama principal una vez verificada. Las horas se registran por actividad en `docs/horas.csv`.

### Uso de inteligencia artificial

Se usaron asistentes de inteligencia artificial, en el grado y las etapas que detalla `docs/uso-de-ia.md`, según lo pedido por el director. Desde noviembre de 2026 la IA escribe el código, y el autor define qué se hace, cuestiona cada propuesta, aprueba los cambios y verifica el resultado.

### Validación

La validación combina pruebas automáticas de la API sobre una base PostgreSQL real, un recorrido automático de punta a punta en navegador y pruebas manuales sobre el sistema publicado, con pagos en el entorno de pruebas de Mercado Pago y escaneos con celulares reales. La estrategia, los criterios de aceptación y la relación con los requerimientos están en el capítulo 08.
