"""Diagrama de estados de la navegación entre pantallas (Larman, cap. 29). Rutas de frontend/src/main.tsx."""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

# Por defecto escribe en docs/memoria/diagramas; se puede pasar otra carpeta como argumento
DESTINO = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parent.parent)

s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 670" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#111">',
     '<defs><marker id="f" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M1 1L9 5L1 9" fill="none" stroke="#111" stroke-width="1.2"/></marker></defs>',
     '<rect width="1120" height="670" fill="#fff"/>']


def estado(x0, y0, x1, y1, nombre):
    s.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" rx="14" fill="#fff" stroke="#111" stroke-width="1.2"/>')
    s.append(f'<text x="{(x0+x1)/2}" y="{(y0+y1)/2+4}" text-anchor="middle">{escape(nombre)}</text>')


def t(d, *etiquetas):
    s.append(f'<path d="{d}" fill="none" stroke="#111" stroke-width="1.1" marker-end="url(#f)"/>')
    for x, y, texto, *a in etiquetas:
        s.append(f'<text x="{x}" y="{y}" font-size="11" text-anchor="{a[0] if a else "start"}">{escape(texto)}</text>')


# superestado: pantallas con el menú; sus subestados heredan las transiciones del menú (fig. 29.5)
s.append('<rect x="280" y="30" width="600" height="540" rx="18" fill="none" stroke="#111" stroke-width="1.2"/>')
s.append('<text x="292" y="50" font-weight="700">ConMenu</text>')

estado(380, 70, 520, 110, 'Catálogo')
estado(620, 70, 760, 110, 'Detalle')
estado(380, 200, 520, 240, 'MisPublicaciones')
estado(620, 200, 760, 240, 'Solicitudes')
estado(380, 330, 520, 370, 'Publicar')
estado(380, 460, 520, 500, 'Operaciones')
estado(620, 460, 760, 500, 'Operación')
estado(20, 130, 150, 170, 'Bienvenida')
estado(20, 330, 150, 370, 'Ingresar')
estado(20, 470, 150, 510, 'Registro')
estado(930, 440, 1090, 480, 'MercadoPago')
estado(930, 560, 1090, 600, 'Escanear')

# estado inicial, bifurcación e historia
s.append('<circle cx="30" cy="60" r="7" fill="#111"/>')
s.append('<path d="M80 52L88 60L80 68L72 60Z" fill="#fff" stroke="#111"/>')
s.append('<circle cx="310" cy="410" r="11" fill="#fff" stroke="#111"/><text x="310" y="414" text-anchor="middle" font-weight="700">H</text>')

t('M37 60H71')
t('M80 68V129', (86, 100, '[primera visita]'))
t('M88 60H330V80H379', (200, 54, '[ya la vio]', 'middle'))
t('M150 150H330V100H379', (156, 144, 'elegirUbicación'))
t('M85 170V329', (91, 250, 'yaTengoCuenta'))

# menú: transiciones que salen del borde del superestado
t('M450 30V69', (456, 54, 'irACatálogo'))
t('M280 220H379', (286, 214, 'irAMisArtículos'))
t('M280 345H379', (286, 339, 'irAPublicar'))
t('M280 480H379', (286, 474, 'irAOperaciones'))

# cuenta: se pide al entrar sin sesión a una pantalla o acción privada; al terminar vuelve a donde estaba (H)
t('M280 300H125V329', (160, 282, 'pedirIngreso'), (160, 295, '[sin sesión]'))
t('M150 362H220V406H298', (156, 378, 'ingresar'))
t('M150 490H240V414H299', (156, 484, 'registrarse'))
t('M50 370V469', (56, 410, 'irARegistro'))
t('M130 469V371', (136, 440, 'irAIngresar'))

# dentro del menú
t('M520 90H619', (570, 84, 'abrirArtículo', 'middle'))
t('M760 90H820V420H690V459', (700, 414, 'reservar [con sesión]'))
t('M520 220H619', (570, 207, 'verSolicitudes', 'middle'), (570, 234, '[administrador]', 'middle'))
t('M450 330V241', (456, 290, 'publicar'))
t('M520 480H619', (570, 474, 'abrirOperación', 'middle'))

# fuera del menú
t('M760 462H929', (845, 456, 'pagar', 'middle'))
t('M930 478H761', (845, 494, 'volver', 'middle'))
t('M670 500V585H929', (676, 545, 'escanear [vendedor]'))
t('M960 560V525H720V501', (840, 519, 'volver', 'middle'))
t('M1060 600V635H450V501', (755, 629, 'verOperaciones', 'middle'))

s.append('</svg>')
open(f'{DESTINO}/navegacion.svg', 'w', encoding='utf-8').write('\n'.join(s))
print('ok')
