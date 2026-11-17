"""Diagrama de paquetes de la arquitectura lógica en capas (Larman, caps. 30 y 31)."""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

# Por defecto escribe en docs/memoria/diagramas; se puede pasar otra carpeta como argumento
DESTINO = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parent.parent)

s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 610" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#111">',
     '<defs><marker id="dep" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M1 1L9 5L1 9" fill="none" stroke="#111" stroke-width="1.1"/></marker></defs>',
     '<rect width="1100" height="610" fill="#fff"/>']


def paquete(x, y, w, h, nombre, tab=None, negrita=False):
    tab = tab or max(70, 8 * len(nombre) + 16)
    s.append(f'<path d="M{x} {y}H{x+tab}V{y+20}H{x}Z" fill="#fff" stroke="#111" stroke-width="1.2"/>')
    s.append(f'<rect x="{x}" y="{y+20}" width="{w}" height="{h}" fill="none" stroke="#111" stroke-width="1.2"/>')
    peso = ' font-weight="700"' if negrita else ''
    s.append(f'<text x="{x+8}" y="{y+15}"{peso}>{escape(nombre)}</text>')


def caja(x, y, w, nombre):
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="30" fill="#fff" stroke="#111"/>')
    s.append(f'<text x="{x+w/2}" y="{y+19}" text-anchor="middle">{escape(nombre)}</text>')


def dependencia(d, etiqueta=None, ex=0, ey=0):
    s.append(f'<path d="{d}" fill="none" stroke="#111" stroke-dasharray="6 4" marker-end="url(#dep)"/>')
    if etiqueta:
        s.append(f'<text x="{ex}" y="{ey}" font-size="11">{escape(etiqueta)}</text>')


# capa de Presentación (frontend)
paquete(20, 20, 1060, 150, 'Presentación', tab=140, negrita=True)
paquete(40, 55, 530, 95, 'pages')
for i, n in enumerate(['Catalogo', 'Publicar', 'Transaccion', 'Escanear', '...']):
    caja(55 + i * 102, 95, 92, n)
for i, n in enumerate(['api', 'sesion', 'ubicacion', 'fotos', 'ui']):
    caja(610 + i * 92, 95, 82, n)

# capa del Dominio (backend: controladores y reglas de negocio)
paquete(20, 230, 1060, 150, 'Dominio', tab=140, negrita=True)
paquete(40, 265, 760, 95, 'routers')
for i, n in enumerate(['usuario_router', 'publicacion_router', 'transaccion_router', 'pago_router', 'institucion_router']):
    caja(55 + i * 148, 305, 138, n)
paquete(850, 265, 210, 95, 'schemas')

# capa de Servicios Técnicos
paquete(20, 440, 1060, 150, 'Servicios Técnicos', tab=160, negrita=True)
paquete(40, 475, 420, 95, 'utils')
for i, n in enumerate(['security', 'pagos', 'fotos']):
    caja(55 + i * 135, 515, 125, n)
paquete(560, 475, 260, 95, 'database')

# dependencias: siempre hacia la capa de abajo o dentro de la misma capa
dependencia('M570 110H609')
dependencia('M651 125V284', '«HTTP»', 658, 205)
dependencia('M800 320H849')
dependencia('M250 380V494')
dependencia('M690 380V494')

s.append('</svg>')
open(f'{DESTINO}/paquetes.svg', 'w', encoding='utf-8').write('\n'.join(s))
print('ok')
