"""Diagrama de despliegue con componentes, con la notación de Larman (cap. 38, figs. 38.4 y 38.5)."""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

# Por defecto escribe en docs/memoria/diagramas; se puede pasar otra carpeta como argumento
DESTINO = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parent.parent)

s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 720" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#111">',
     '<defs><marker id="dep" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M1 1L9 5L1 9" fill="none" stroke="#111" stroke-width="1.1"/></marker></defs>',
     '<rect width="1180" height="720" fill="#fff"/>']
P = 12  # profundidad del cubo del nodo


def nodo(x, y, w, h, nombre):
    s.append(f'<path d="M{x} {y}L{x+P} {y-P}H{x+w+P}V{y+h-P}L{x+w} {y+h}" fill="#fff" stroke="#111" stroke-width="1.2"/>')
    s.append(f'<path d="M{x+w} {y}L{x+w+P} {y-P}" fill="none" stroke="#111" stroke-width="1.2"/>')
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff" stroke="#111" stroke-width="1.2"/>')
    s.append(f'<text x="{x+10}" y="{y+20}" text-decoration="underline">{escape(nombre)}</text>')


def componente(x, y, w, h, estereotipo, nombre):
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff" stroke="#111"/>')
    for dy in (10, 28):
        s.append(f'<rect x="{x-8}" y="{y+dy}" width="16" height="10" fill="#fff" stroke="#111"/>')
    s.append(f'<text x="{x+w/2+4}" y="{y+18}" text-anchor="middle" font-size="11">«{escape(estereotipo)}»</text>')
    s.append(f'<text x="{x+w/2+4}" y="{y+33}" text-anchor="middle" text-decoration="underline">{escape(nombre)}</text>')


def interfaz(xc, yc, xbase, nombre, tx, ty, ancla='middle', ybase=None):
    """Piruleta: un círculo unido al componente que ofrece la interfaz (de costado o, con ybase, de arriba o abajo)."""
    tallo = f'M{xc} {ybase}V{yc}' if ybase is not None else f'M{xbase} {yc}H{xc}'
    s.append(f'<path d="{tallo}" stroke="#111"/>')
    s.append(f'<circle cx="{xc}" cy="{yc}" r="5" fill="#fff" stroke="#111"/>')
    s.append(f'<text x="{tx}" y="{ty}" text-anchor="{ancla}" font-size="11">{escape(nombre)}</text>')


def dependencia(d):
    s.append(f'<path d="{d}" fill="none" stroke="#111" stroke-dasharray="6 4" marker-end="url(#dep)"/>')


nodo(30, 230, 270, 260, ': Dispositivo del usuario')
componente(58, 270, 222, 190, 'browser', ':Navegador')
componente(88, 340, 172, 50, 'SPA', ':Frontend')

nodo(370, 60, 420, 600, ': Vercel')
componente(430, 110, 330, 60, 'archivos estáticos', ':FrontendCompilado')
componente(430, 270, 330, 170, 'función serverless', ':Backend')
componente(430, 560, 330, 60, 'planificador', ':VercelCron')

nodo(870, 60, 280, 260, ': Supabase')
componente(910, 110, 220, 60, 'almacenamiento', ':Storage')
componente(910, 230, 220, 60, 'database', ':PostgreSQL')

nodo(870, 400, 280, 260, ': Mercado Pago')
componente(910, 450, 220, 60, 'servicio', ':APIDePagos')
componente(910, 570, 220, 60, 'servicio', ':CheckoutPro')

# interfaces que ofrece cada componente
interfaz(407, 140, 422, 'HTTPS', 404, 126, 'end')
interfaz(407, 330, 422, 'API REST', 404, 316, 'end')
interfaz(785, 380, 760, 'webhook', 792, 370, 'start')
interfaz(1020, 92, None, 'HTTPS', 1030, 90, 'start', ybase=110)
interfaz(888, 260, 902, 'SQL', 885, 246, 'end')
interfaz(888, 480, 902, 'API REST', 885, 500, 'end')
interfaz(1020, 645, None, 'HTTPS', 1030, 650, 'start', ybase=630)

# dependencias hacia las interfaces que se usan
dependencia('M260 352L403 144')          # la SPA se descarga del hosting estático
dependencia('M260 372L401 330')          # la SPA llama a la API REST
dependencia('M170 270V30H1020V85')  # la SPA sube las fotos a Storage con una URL firmada
dependencia('M170 460V700H1020V652')  # el comprador paga en Checkout Pro
dependencia('M430 590H398V337')          # el cron llama a GET /vencer
dependencia('M760 280L850 200V92H1013')          # el backend firma las URL de subida
dependencia('M760 300L882 258')          # el backend consulta la base
dependencia('M760 425L882 478')          # el backend crea preferencias, consulta pagos y pide devoluciones
dependencia('M905 452L790 385')          # Mercado Pago avisa los pagos al webhook

s.append('</svg>')
open(f'{DESTINO}/despliegue.svg', 'w', encoding='utf-8').write('\n'.join(s))
print('ok')
