"""Modelo de datos con el perfil UML de modelado de datos (Larman, cap. 34, fig. 34.2). Columnas y tipos de schema.sql."""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

# Por defecto escribe en docs/memoria/diagramas; se puede pasar otra carpeta como argumento
DESTINO = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parent.parent)

s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 670" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#111">',
     '<rect width="1100" height="670" fill="#fff"/>']


def tabla(x, y, w, nombre, columnas):
    h = 40 + 8 + 16 * len(columnas)
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff" stroke="#111" stroke-width="1.2"/>')
    s.append(f'<path d="M{x} {y+40}H{x+w}" stroke="#111"/>')
    s.append(f'<text x="{x+w/2}" y="{y+16}" text-anchor="middle" font-size="11">«Table»</text>')
    s.append(f'<text x="{x+w/2}" y="{y+32}" text-anchor="middle" font-weight="700">{escape(nombre)}</text>')
    for i, c in enumerate(columnas):
        s.append(f'<text x="{x+8}" y="{y+60+16*i}" font-size="11.5">{escape(c)}</text>')
    return y + h


def asociacion(d, textos):
    s.append(f'<path d="{d}" fill="none" stroke="#111" stroke-width="1.1"/>')
    for x, y, t, *it in textos:
        estilo = ' font-style="italic"' if it else ''
        s.append(f'<text x="{x}" y="{y}"{estilo}>{escape(t)}</text>')


tabla(40, 40, 250, 'usuarios', [
    '«PK» id : uuid', 'email : varchar(255)', 'nombre : varchar(100)', 'apellido : varchar(100)',
    'password_hash : text', 'telefono : varchar(20)', 'rol : varchar(20)', 'fecha_registro : timestamptz',
    'intentos_fallidos : integer', 'bloqueado_hasta : timestamptz'])
tabla(420, 40, 260, 'publicaciones', [
    '«PK» id : uuid', '«FK» vendedor_id : uuid', '«FK» institucion_id : integer', 'titulo : varchar(100)',
    'descripcion : text', 'categoria : varchar(20)', 'talle : varchar(10)', 'tipo : varchar(10)',
    'precio : numeric(10, 2)', 'estado : varchar(20)', 'aviso : text', 'imagenes_urls : text[]',
    'fecha_publicacion : timestamptz'])
tabla(830, 40, 230, 'instituciones', [
    '«PK» id : serial', 'nombre : varchar(150)', 'ciudad : varchar(100)', 'provincia : varchar(100)',
    'fecha_creacion : timestamptz'])
tabla(420, 380, 260, 'transacciones_escrow', [
    '«PK» id : uuid', '«FK» publicacion_id : uuid', '«FK» comprador_id : uuid', '«FK» vendedor_id : uuid',
    'monto : numeric(10, 2)', 'comision_plataforma : numeric(10, 2)', 'id_pago_externo : text',
    'estado_pago : varchar(20)', 'qr_token : uuid', 'fecha_creacion : timestamptz', 'fecha_liberacion : timestamptz'])
tabla(830, 380, 230, 'solicitudes_institucion', [
    '«PK» id : uuid', '«FK» publicacion_id : uuid', '«FK» solicitante_id : uuid', 'nombre : varchar(150)',
    'ciudad : varchar(100)', 'provincia : varchar(100)', 'estado : varchar(20)', 'fecha_creacion : timestamptz'])

# multiplicidad 1 = la clave ajena es obligatoria (NOT NULL); 0..1 = puede quedar vacía
asociacion('M290 100H420', [(300, 94, '1'), (300, 114, 'vendedor', 1), (390, 94, '0..*')])
asociacion('M680 100H830', [(686, 94, '0..*'), (802, 94, '0..1')])
asociacion('M550 296V380', [(560, 312, '1'), (556, 376, '0..*')])
asociacion('M120 248V440H420', [(130, 264, '1'), (126, 280, 'comprador', 1), (390, 434, '0..*')])
asociacion('M220 248V500H420', [(230, 264, '1'), (226, 280, 'vendedor', 1), (390, 494, '0..*')])
asociacion('M680 270H760V420H830', [(690, 262, '1'), (802, 414, '0..1')])
asociacion('M60 248V640H940V556', [(70, 264, '1'), (66, 296, 'solicitante', 1), (946, 572, '0..*')])

# rombo relleno del lado de la tabla referenciada: la clave ajena es obligatoria y no puede existir
# una fila sin la fila relacionada (Larman, fig. 34.2)
def rombo(x, y, vertical):
    d = f'M{x} {y}L{x+5} {y+8}L{x} {y+16}L{x-5} {y+8}Z' if vertical else f'M{x} {y}L{x+8} {y-5}L{x+16} {y}L{x+8} {y+5}Z'
    s.append(f'<path d="{d}" fill="#111" stroke="#111"/>')


for x, y, v in [(290, 100, False), (680, 270, False), (550, 296, True), (120, 248, True), (220, 248, True), (60, 248, True)]:
    rombo(x, y, v)

s.append('</svg>')
open(f'{DESTINO}/modelo-de-datos.svg', 'w', encoding='utf-8').write('\n'.join(s))
print('ok')
