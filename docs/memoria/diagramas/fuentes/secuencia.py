"""Genera los diagramas de secuencia de la memoria con la notación de Larman (cap. 15).

Las instancias llevan el nombre subrayado (fig. 15.5). Los módulos de Python, que se usan
llamando a sus funciones, se dibujan como clases sin subrayar (fig. 15.27).
"""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

# Por defecto escribe en docs/memoria/diagramas; se puede pasar otra carpeta como argumento
DESTINO = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parent.parent)

AW = 5  # medio ancho de la caja de activación


def diagrama(participantes, alto, activaciones, mensajes, notas=(), marcos=()):
    X = {k: x for k, x, *_ in participantes}
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 {alto}" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#111">',
         '<defs><marker id="llena" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0 1L9 5L0 9Z" fill="#111"/></marker>',
         '<marker id="abierta" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M1 1L9 5L1 9" fill="none" stroke="#111" stroke-width="1.1"/></marker></defs>',
         f'<rect width="1100" height="{alto}" fill="#fff"/>']
    for k, x, nombre, subrayado in participantes:
        deco = ' text-decoration="underline"' if subrayado else ''
        if k == 'actor':
            s.append(f'<g fill="none" stroke="#111" stroke-width="1.4"><circle cx="{x}" cy="16" r="8"/><path d="M{x} 24V42M{x-12} 30H{x+12}M{x} 42L{x-10} 56M{x} 42L{x+10} 56"/></g>')
            s.append(f'<text x="{x}" y="72" text-anchor="middle"{deco}>{escape(nombre)}</text>')
            y0 = 78
        else:
            s.append(f'<rect x="{x-80}" y="30" width="160" height="32" fill="#fff" stroke="#111" stroke-width="1.2"/>')
            s.append(f'<text x="{x}" y="51" text-anchor="middle"{deco}>{escape(nombre)}</text>')
            y0 = 62
        s.append(f'<path d="M{x} {y0}V{alto-10}" stroke="#111" stroke-dasharray="4 4"/>')
    for (x0, y0, x1, y1, etiqueta) in marcos:
        s.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="none" stroke="#111"/>')
        s.append(f'<text x="{x1-6}" y="{y1-6}" text-anchor="end">{escape(etiqueta)}</text>')
    for (k, y0, y1, *desv) in activaciones:
        x = X[k] + (desv[0] if desv else 0)
        s.append(f'<rect x="{x-AW}" y="{y0}" width="{2*AW}" height="{y1-y0}" fill="#fff" stroke="#111"/>')
    for tipo, a, b, y, texto, *desv in mensajes:
        if tipo == 'self':
            x = X[a] + AW
            s.append(f'<path d="M{x} {y}H{x+40}V{y+18}H{x+10}" fill="none" stroke="#111" marker-end="url(#llena)"/>')
            s.append(f'<text x="{x+46}" y="{y+13}">{escape(texto)}</text>')
            continue
        xa, xb = X[a] + (desv[0] if desv else 0), X[b]
        sentido = 1 if xb > xa else -1
        ini = xa + sentido * (AW if a != 'actor' else 0)
        fin = xb - sentido * (AW if b != 'actor' else 0)
        estilo = 'stroke-dasharray="6 4" marker-end="url(#abierta)"' if tipo == 'ret' else 'marker-end="url(#llena)"'
        s.append(f'<path d="M{ini} {y}H{fin}" stroke="#111" {estilo}/>')
        renglones = texto.split('\n')
        for i, r in enumerate(renglones):
            s.append(f'<text x="{(xa+xb)/2}" y="{y-5-14*(len(renglones)-1-i)}" text-anchor="middle">{escape(r)}</text>')
    for (x, y, w, lineas, ancla) in notas:
        h = 10 + 15 * len(lineas)
        s.append(f'<path d="M{x} {y}H{x+w-10}L{x+w} {y+10}V{y+h}H{x}Z M{x+w-10} {y}V{y+10}H{x+w}" fill="#fff" stroke="#111"/>')
        for i, l in enumerate(lineas):
            s.append(f'<text x="{x+6}" y="{y+17+15*i}" font-size="11">{escape(l)}</text>')
        if ancla:
            borde = x + w if ancla[0] > x + w else x
            s.append(f'<path d="M{borde} {y+h/2}L{ancla[0]} {ancla[1]}" stroke="#111" stroke-dasharray="3 3"/>')
    s.append('</svg>')
    return '\n'.join(s)


pago = diagrama(
    [('actor', 60, ': Comprador', True), ('pant', 230, ':PantallaDeOperación', True),
     ('trans', 420, 'transaccion_router', False), ('webhook', 610, 'pago_router', False),
     ('pagos', 800, 'pagos', False), ('mp', 990, ':MercadoPago', True)],
    780,
    activaciones=[('pant', 90, 340), ('pant', 630, 745), ('trans', 120, 315), ('trans', 675, 700),
                  ('webhook', 400, 600), ('pagos', 210, 290), ('pagos', 430, 455), ('pagos', 485, 560),
                  ('mp', 240, 265), ('mp', 370, 400), ('mp', 510, 535), ('mp', 625, 635)],
    mensajes=[('msg', 'actor', 'pant', 90, 'pagar()'),
              ('msg', 'pant', 'trans', 120, 'iniciar_pago(id)'),
              ('msg', 'trans', 'pagos', 210, 'crear_preferencia(id, título, monto)'),
              ('msg', 'pagos', 'mp', 240, 'crearPreferencia(preferencia)'),
              ('ret', 'mp', 'pagos', 265, 'initPoint'),
              ('ret', 'pagos', 'trans', 290, 'urlDePago'),
              ('ret', 'trans', 'pant', 315, 'urlDePago'),
              ('ret', 'pant', 'actor', 340, 'urlDePago'),
              ('msg', 'actor', 'mp', 370, 'pagar(medioDePago)'),
              ('msg', 'mp', 'webhook', 400, 'webhook_mercadopago(aviso)'),
              ('msg', 'webhook', 'pagos', 430, 'firma_valida(firma, idAviso, idPago)'),
              ('ret', 'pagos', 'webhook', 455, 'verdadero'),
              ('msg', 'webhook', 'pagos', 485, 'obtener_pago(idPago)'),
              ('msg', 'pagos', 'mp', 510, 'consultarPago(idPago)'),
              ('ret', 'mp', 'pagos', 535, 'pago'),
              ('ret', 'pagos', 'webhook', 560, 'pago'),
              ('msg', 'mp', 'pant', 630, 'volver(idOperación)'),
              ('msg', 'pant', 'trans', 675, 'obtener_mis_transacciones()'),
              ('ret', 'trans', 'pant', 700, 'operaciones'),
              ('ret', 'pant', 'actor', 745, 'QR de entrega y contacto')],
    notas=[(437, 565, 160, ['Si el pago está aprobado,', 'la registra como retenida.'], (605, 585))],
    marcos=[(150, 650, 520, 720, '* [cada 5 s, hasta que esté retenida]')])

cancelar = diagrama(
    [('actor', 70, ': Comprador o Vendedor', True), ('pant', 270, ':PantallaDeOperación', True),
     ('trans', 510, 'transaccion_router', False), ('pagos', 750, 'pagos', False),
     ('mp', 990, ':MercadoPago', True)],
    450,
    activaciones=[('pant', 90, 410), ('trans', 120, 380), ('trans', 195, 345, 8),
                  ('pagos', 265, 330), ('mp', 295, 320)],
    mensajes=[('msg', 'actor', 'pant', 90, 'cancelar()'),
              ('msg', 'pant', 'trans', 120, 'cancelar_transaccion(id)'),
              ('self', 'trans', None, 190, '_cancelar(id, idPublicación, estado, idPago)'),
              ('msg', 'trans', 'pagos', 265, '[estado = retenido]\nreembolsar(idPago, claveDeIdempotencia)', 8),
              ('msg', 'pagos', 'mp', 295, 'crearDevolución(idPago,\nclaveDeIdempotencia)'),
              ('ret', 'mp', 'pagos', 320, 'devolución'),
              ('ret', 'trans', 'pant', 380, 'nuevoEstado'),
              ('ret', 'pant', 'actor', 410, 'operación cancelada')],
    notas=[(285, 235, 205, ['Después de la devolución, actualiza', 'la operación (reembolsada o', 'cancelada) y la publicación', '(disponible). Si Mercado Pago', 'rechaza, no se confirma nada.'], (510, 300))])

open(f'{DESTINO}/secuencia-pagar.svg', 'w', encoding='utf-8').write(pago)
open(f'{DESTINO}/secuencia-cancelar.svg', 'w', encoding='utf-8').write(cancelar)
print('ok')
