# 01 · Requerimientos

> Borrador. Basado en el protocolo final (presentado el 09/09/2026, con correcciones del 14/09) y en las decisiones [001](../decisiones/001-stack-frontend.md) y [002](../decisiones/002-retencion-de-fondos.md). Los objetivos específicos (OE) están en el [capítulo 00](00-introduccion-objetivos-metodologia.md), los casos de uso (CU) en el [capítulo 06](06-casos-de-uso.md) y los casos de prueba en el [capítulo 08](08-plan-de-pruebas.md).

## Actores

- **Visitante:** persona sin sesión. Solo puede navegar el catálogo.
- **Comprador o receptor:** usuario registrado que reserva un artículo.
- **Vendedor o donante:** usuario registrado que publica un artículo. Un mismo usuario cumple ambos roles en distintas operaciones.
- **Administrador:** gestiona el listado de instituciones y resuelve las solicitudes de colegios.
- **Mercado Pago:** sistema externo que procesa los pagos (sandbox en el prototipo).
- **Planificador de tareas:** sistema externo que dispara los vencimientos una vez por día. En el prototipo es Vercel Cron.

## Requerimientos funcionales del prototipo

| Código | Requerimiento | Objetivo | Caso de uso | Estado |
|---|---|---|---|---|
| RF-01 | Registro e inicio de sesión con correo y contraseña | OE-4, OE-5 | CU-01, CU-02 | Hecho |
| RF-02 | Publicar artículos de tipo venta (precio > 0) o donación (sin precio), con categoría, talle, institución e imágenes | OE-4 | CU-04 | Hecho |
| RF-03 | Catálogo público con filtros combinables: provincia, ciudad, institución, categoría, tipo y talle | OE-3 | CU-03 | Hecho |
| RF-04 | Ver y dar de baja las publicaciones propias | OE-4 | CU-06 | Hecho |
| RF-05 | Iniciar una compra o solicitud de donación, que reserva el artículo | OE-5 | CU-07 | Hecho |
| RF-06 | Pagar mediante billetera virtual; los fondos quedan retenidos y se cobra una comisión del 5% en las ventas | OE-5 | CU-08 | Hecho (probado en sandbox) |
| RF-07 | Generar un código QR para el comprador; el vendedor lo escanea en el encuentro y se liberan los fondos | OE-6 | CU-10, CU-11 | Hecho (cámara probada en celulares reales el 09/11/2026) |
| RF-08 | Compartir los datos de contacto de la contraparte una vez confirmado el pago | OE-7 | CU-09 | Hecho |
| RF-09 | Cancelar una operación no concretada, con reembolso si había pago | OE-5 | CU-12 | Hecho (devolución verificada con dinero real, ver cap. 04) |
| RF-10 | Vencer automáticamente las reservas sin pagar (24 h) y las operaciones sin escaneo (7 días en ventas, 4 en donaciones) | OE-5 | CU-14 | Hecho |
| RF-11 | Historial de operaciones del usuario | OE-5 | CU-13 | Hecho |
| RF-12 | Alta, edición y baja de instituciones por un administrador | OE-3 | CU-15 | Hecho (solo por API, sin pantalla) |
| RF-13 | Pedir el alta de un colegio que no está en la lista al publicar (funcionalidad opcional del protocolo) | OE-3, OE-4 | CU-05, CU-16 | Hecho |

## Funcionalidades opcionales no implementadas

Alertas automáticas por correo, panel de administración con reclamos, calificación y reputación. Fuera de alcance: envíos por correo y pagos fuera de las billeteras virtuales.

## Reglas de negocio

| Código | Regla |
|---|---|
| RN-01 | Una venta tiene precio mayor a 0; una donación no tiene precio ni comisión. |
| RN-02 | Un usuario no puede comprar su propio artículo. |
| RN-03 | Un artículo reservado no puede ser tomado por otro comprador, incluso si dos lo intentan al mismo tiempo. |
| RN-04 | El código QR solo lo ve el comprador. El vendedor nunca tiene acceso a él. |
| RN-05 | Solo el vendedor de la operación puede escanear el QR. |
| RN-06 | En una venta, el QR solo se puede escanear con el pago retenido. En una donación, desde que se inicia la operación. |
| RN-07 | El escaneo del QR es la única prueba de entrega. Una vez escaneado, la operación no se puede cancelar. |
| RN-08 | Sin escaneo, cualquiera de las partes puede cancelar y el dinero vuelve al comprador. |
| RN-09 | Si pasan 7 días sin escaneo (4 en las donaciones), la operación se cancela y, si había pago, se reembolsa automáticamente. Una venta reservada y no pagada se libera a las 24 horas. |
| RN-10 | Los datos de contacto se comparten recién con el pago retenido (ventas) o con la operación iniciada (donaciones). |
| RN-11 | Una publicación con una operación en curso no se puede dar de baja. |
| RN-12 | Un usuario puede tener como máximo 3 donaciones pendientes de retirar a la vez. Las ventas no tienen tope. |
| RN-13 | Una venta tiene precio mayor a 0 y una donación precio 0; la base de datos lo garantiza con una restricción. |
| RN-14 | Una publicación tiene como máximo 5 fotos (JPG, PNG o WebP, hasta 5 MB cada una), y todas tienen que haber sido subidas por su autor. |
| RN-15 | Una publicación que pide el alta de un colegio no aparece en el catálogo hasta que se resuelve la solicitud. Si el colegio se acepta, se publica. Si ya existía con otro nombre, se le asigna el correcto, se publica y se avisa al dueño. Si no existe, queda en borrador para que el dueño elija otro. |
| RN-16 | El catálogo y el detalle son públicos. Reservar, publicar y ver las operaciones propias requieren sesión. |

## Requerimientos no funcionales

| Código | Atributo | Requerimiento | Justificación |
|---|---|---|---|
| RNF-01 | Seguridad | Las contraseñas se guardan con bcrypt y salt propio; nunca en texto plano | Una filtración de la base no debe exponer las contraseñas |
| RNF-02 | Seguridad | La sesión usa un JWT firmado con HS256 que vence a las 2 horas | Limita el daño de un token robado |
| RNF-03 | Seguridad | Después de 5 intentos de login fallidos seguidos, la cuenta se bloquea 15 minutos | Dificulta probar contraseñas por fuerza bruta |
| RNF-04 | Seguridad | Sin sesión válida una ruta privada responde 401, y sin el rol o la pertenencia necesarios responde 403. La API solo acepta pedidos del navegador desde el dominio del frontend | Cada operación solo la hacen quienes corresponde |
| RNF-05 | Seguridad | Los errores internos no exponen detalles al cliente; quedan en los logs | No dar información útil a un atacante |
| RNF-06 | Consistencia | Los cambios de estado de dinero y artículos se hacen en una única transacción de base de datos con bloqueo de fila; un artículo no puede tener dos operaciones en curso | Se maneja dinero: no pueden quedar estados intermedios |
| RNF-07 | Integridad de pagos | Un aviso de pago solo se acepta con firma HMAC-SHA256 válida y confirmando el pago contra Mercado Pago; procesarlo más de una vez no cambia el resultado | Nadie debe poder simular un pago, y Mercado Pago reintenta los avisos |
| RNF-08 | Usabilidad | La interfaz funciona sin desplazamiento horizontal en anchos de 390, 820 y 1440 píxeles | El escaneo ocurre en el encuentro, con el celular |
| RNF-09 | Compatibilidad | El escaneo funciona con la cámara de un celular desde el navegador, sin instalar una aplicación | Reduce la fricción en el encuentro |
| RNF-10 | Desempeño | El catálogo responde en menos de 3 segundos con 100 publicaciones (meta a confirmar, todavía sin medir) | El catálogo es la operación más frecuente |
| RNF-11 | Costo | La infraestructura funciona en los planes gratuitos de Supabase y Vercel | Factibilidad económica del protocolo |

## Restricciones

| Código | Restricción |
|---|---|
| R-01 | Dedicación estimada de 200 horas, un único desarrollador y entrega prevista para el 26/12/2026 |
| R-02 | Prototipo académico: los pagos operan en el sandbox de Mercado Pago, porque custodiar fondos de terceros con dinero real tiene exigencias regulatorias (BCRA y UIF, ver decisión 002 y capítulo 04) |
| R-03 | Infraestructura sin costo: Vercel limita las tareas programadas a una ejecución diaria en el plan gratuito, así que los vencimientos se procesan una vez por día |
| R-04 | Backend monolítico y arquitectura cliente-servidor, según lo definido en el protocolo |
| R-05 | El intercambio es siempre presencial; no se integran servicios de envío |
| R-06 | Los pagos se hacen únicamente mediante billeteras virtuales; en el prototipo, Mercado Pago |
