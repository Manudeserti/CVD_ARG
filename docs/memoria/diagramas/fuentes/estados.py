"""Genera los diagramas de estados de la memoria con la notación de Larman (cap. 29)."""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

# Por defecto escribe en docs/memoria/diagramas; se puede pasar otra carpeta como argumento
DESTINO = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parent.parent)


def svg(ancho, alto, estados, transiciones, extras=''):
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#111">',
         '<defs><marker id="flecha" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M1 1L9 5L1 9" fill="none" stroke="#111" stroke-width="1.2"/></marker></defs>',
         f'<rect width="{ancho}" height="{alto}" fill="#fff"/>', extras]
    for nombre, x0, y0, x1, y1 in estados:
        s.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" rx="14" fill="#fff" stroke="#111" stroke-width="1.2"/>')
        s.append(f'<text x="{(x0+x1)/2}" y="{(y0+y1)/2+4}" text-anchor="middle">{escape(nombre)}</text>')
    for camino, etiquetas in transiciones:
        s.append(f'<path d="{camino}" fill="none" stroke="#111" stroke-width="1.1" marker-end="url(#flecha)"/>')
        for x, y, texto, *ancla in etiquetas:
            a = ancla[0] if ancla else 'start'
            s.append(f'<text x="{x}" y="{y}" text-anchor="{a}">{escape(texto)}</text>')
    s.append('</svg>')
    return '\n'.join(s)


inicial = lambda x, y: f'<circle cx="{x}" cy="{y}" r="7" fill="#111"/>'

operacion = svg(1100, 370,
    estados=[('Pendiente', 140, 180, 280, 220), ('Retenido', 490, 60, 630, 100), ('Liberado', 830, 60, 970, 100),
             ('Cancelado', 490, 300, 630, 340), ('Reembolsado', 830, 300, 970, 340)],
    transiciones=[
        ('M67 200H139', [(103, 192, 'reservar', 'middle')]),
        ('M280 190L489 92', [(330, 128, 'pagoAprobado')]),
        ('M630 80H829', [(730, 72, 'confirmarEntrega', 'middle')]),
        ('M210 180V25H900V59', [(560, 19, 'confirmarEntrega [donación]', 'middle')]),
        ('M280 210L489 318', [(345, 288, 'cancelar')]),
        ('M630 95L830 300', [(742, 205, 'cancelar / reembolsar')]),
        ('M630 320H829', [(730, 312, 'pagoAprobado / reembolsar', 'middle')]),
    ],
    extras=inicial(60, 200))

publicacion = svg(1100, 480,
    estados=[('PendienteDeColegio', 230, 180, 390, 220), ('Borrador', 230, 300, 390, 340), ('Disponible', 510, 80, 650, 120),
             ('Reservado', 770, 80, 910, 120), ('Vendido', 770, 220, 910, 260), ('Baja', 370, 420, 510, 460)],
    transiciones=[
        ('M57 200H121', [(89, 192, 'publicar', 'middle')]),
        ('M138 200H229', [(184, 193, '[colegio nuevo]', 'middle')]),
        ('M130 192V100H509', [(330, 93, '[colegio en la lista]', 'middle')]),
        ('M390 190L529 121', [(440, 192, 'resolverSolicitud'), (440, 206, '[aceptada o duplicada]')]),
        ('M310 220V299', [(318, 265, 'resolverSolicitud [rechazada]')]),
        ('M390 320H580V121', [(470, 313, 'elegirColegio', 'middle')]),
        ('M650 95H769', [(710, 88, 'reservar', 'middle')]),
        ('M770 110H651', [(710, 128, 'cancelar', 'middle')]),
        ('M840 120V219', [(850, 175, 'confirmarEntrega')]),
        ('M440 370V419', [(450, 400, 'darDeBaja')]),
    ],
    # superestado SinReserva: sus tres subestados heredan darDeBaja (Larman, fig. 29.5); "publicar" llega a una
    # bifurcación (rombo) que elige el subestado según el colegio
    extras=inicial(50, 200)
    + '<rect x="180" y="40" width="520" height="330" rx="18" fill="none" stroke="#111" stroke-width="1.2"/>'
    + '<text x="196" y="62" font-weight="700">SinReserva</text>'
    + '<path d="M130 192L138 200L130 208L122 200Z" fill="#fff" stroke="#111"/>')

open(f'{DESTINO}/estados-operacion.svg', 'w', encoding='utf-8').write(operacion)
open(f'{DESTINO}/estados-publicacion.svg', 'w', encoding='utf-8').write(publicacion)
print('ok')
