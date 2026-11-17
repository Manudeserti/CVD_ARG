"""Genera gantt.svg. Para actualizarlo, cambiar FECHA_INFORME y TAREAS y volver a correrlo."""
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

FECHA_INFORME = date(2026, 11, 9)
INICIO, FIN = date(2026, 5, 1), date(2026, 12, 31)
ENTREGA = date(2026, 12, 26)
PAUSA = (date(2026, 8, 22), date(2026, 11, 2))

d = lambda dia, mes: date(2026, mes, dia)  # noqa: E731

# nombre, estado, depende de, previsto en el protocolo, trabajado, reprogramado
TAREAS = [
    ("1. Relevamiento y especificación", "Demorada", "–", (d(21, 9), d(1, 10)), [(d(28, 5), d(14, 9)), (d(2, 11), d(9, 11))], (d(10, 11), d(13, 11))),
    ("2. Arquitectura, datos y UI/UX", "Demorada", "1", (d(1, 10), d(15, 10)), [(d(13, 8), d(13, 8)), (d(2, 11), d(2, 11)), (d(9, 11), d(9, 11))], (d(10, 11), d(13, 11))),
    ("3. Backend y API", "Finalizada", "2", (d(15, 10), d(3, 11)), [(d(9, 8), d(22, 8)), (d(2, 11), d(9, 11))], None),
    ("4. Módulo transaccional", "Finalizada", "3", (d(3, 11), d(15, 11)), [(d(14, 8), d(16, 8)), (d(2, 11), d(3, 11))], None),
    ("5. Validación QR", "Finalizada", "3, 4", (d(15, 11), d(25, 11)), [(d(14, 8), d(14, 8)), (d(9, 11), d(9, 11))], None),
    ("6. Frontend responsive", "Finalizada", "3", (d(25, 11), d(12, 12)), [(d(9, 11), d(9, 11))], None),
    ("7. Testing y despliegue", "En curso", "4, 5, 6", (d(12, 12), d(22, 12)), [(d(2, 11), d(9, 11))], (d(10, 11), d(5, 12))),
    ("8a. Marco teórico y estado del arte", "Demorada", "–", None, [], (d(10, 11), d(30, 11))),
    ("8b. Memoria", "En curso", "1, 2, 7, 8a", (d(22, 12), d(26, 12)), [(d(2, 11), d(9, 11))], (d(10, 11), d(22, 12))),
    ("8c. Manuales de usuario y técnico", "En curso", "6, 7", (d(22, 12), d(26, 12)), [(d(2, 11), d(2, 11))], (d(23, 11), d(15, 12))),
]
# Camino crítico (Instructivo 7.9.2): tareas sin holgura, cuya demora corre la entrega.
# 7 tiene que terminar para cerrar la memoria (8b), y sin memoria no hay entrega.
CRITICAS = ("7.", "8b.")
ROJO = "#b3261e"
HITOS = [
    (d(14, 10), "1.er informe previsto (no presentado)"),
    (d(13, 11), "Envío al director"),
    (d(19, 11), "Informes de avance"),
    (ENTREGA, "Entrega final"),
]

COLOR = {"Finalizada": "#2f7d4f", "En curso": "#2469a6", "Demorada": "#c8641e", "Pendiente": "#8a8f98"}
X0, ANCHO, FILA, Y0 = 410, 1050, 44, 92
ALTO_HITOS = 66
MESES = ["Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


def x(fecha):
    return X0 + (fecha - INICIO).days / (FIN - INICIO).days * ANCHO


def barra(desde, hasta, y, alto, **atributos):
    izquierda, derecha = x(desde), max(x(hasta), x(desde) + 5)
    extras = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in atributos.items())
    return f'<rect x="{izquierda:.1f}" y="{y}" width="{derecha - izquierda:.1f}" height="{alto}" {extras}/>'


def texto(px, py, contenido, **atributos):
    extras = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in atributos.items())
    return f'<text x="{px:.1f}" y="{py}" {extras}>{escape(contenido)}</text>'


alto_total = Y0 + FILA * len(TAREAS) + ALTO_HITOS + 120
partes = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1480 {alto_total}" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="#17233b">',
    '<defs><pattern id="rayas" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="7" height="7" fill="#fff"/><rect width="3" height="7" fill="#c8641e"/></pattern></defs>',
    f'<rect width="1480" height="{alto_total}" fill="#fff"/>',
    texto(20, 32, "Trabajo Final CVD: diagrama de Gantt actualizado", font_size=20, font_weight=700),
    texto(20, 54, f"Situación al {FECHA_INFORME:%d/%m/%Y}. Responsable de todas las tareas: Manuel Deserti. Entrega prevista: {ENTREGA:%d/%m/%Y}."),
    texto(20, Y0 - 8, "Tarea", font_weight=700),
    texto(268, Y0 - 8, "Estado", font_weight=700),
    texto(346, Y0 - 8, "Depende", font_weight=700),
]

fondo = FILA * len(TAREAS) + ALTO_HITOS
partes.append(barra(PAUSA[0], PAUSA[1], Y0, fondo, fill="#eceef2"))
partes.append(texto((x(PAUSA[0]) + x(PAUSA[1])) / 2, Y0 + 7 * FILA + 27, "Pausa", text_anchor="middle", fill="#6a7180"))

for numero, mes in enumerate(MESES, start=5):
    inicio_mes = date(2026, numero, 1)
    partes.append(f'<line x1="{x(inicio_mes):.1f}" y1="{Y0 - 4}" x2="{x(inicio_mes):.1f}" y2="{Y0 + fondo}" stroke="#d5d9e0"/>')
    partes.append(texto(x(inicio_mes) + 5, Y0 - 8, mes, font_weight=700))

for fila, (nombre, estado, depende, previsto, trabajado, nuevo) in enumerate(TAREAS):
    y = Y0 + fila * FILA
    partes.append(f'<line x1="20" y1="{y}" x2="{X0 + ANCHO}" y2="{y}" stroke="#e3e6ec"/>')
    partes.append(texto(20, y + 27, nombre))
    partes.append(texto(268, y + 27, estado, fill=COLOR[estado], font_weight=700))
    partes.append(texto(346, y + 27, depende))
    if previsto:
        partes.append(barra(*previsto, y + 7, 9, fill="#a8afbc"))
    for desde, hasta in trabajado:
        partes.append(barra(desde, hasta, y + 20, 15, fill=COLOR["Finalizada"] if estado == "Finalizada" else COLOR["En curso"]))
    if nuevo:
        critica = nombre.startswith(CRITICAS)
        partes.append(barra(*nuevo, y + 20, 15, fill="url(#rayas)", stroke=ROJO if critica else "#c8641e", stroke_width=2.5 if critica else 1))

# Flechas del camino crítico: fin de 7 → fin de 8b → entrega
fila = {nombre.split(" ")[0]: i for i, (nombre, *_) in enumerate(TAREAS)}
fin = {nombre.split(" ")[0]: nuevo[1] for nombre, _, _, _, _, nuevo in TAREAS if nuevo}
y7, y8b = Y0 + fila["7."] * FILA + 35, Y0 + fila["8b."] * FILA + 20
y_entrega = Y0 + len(TAREAS) * FILA + 7
partes.append(f'<defs><marker id="punta" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="{ROJO}"/></marker></defs>')
partes.append(f'<path d="M{x(fin["7."]):.1f} {y7}V{y8b - 2}" stroke="{ROJO}" stroke-width="2" fill="none" marker-end="url(#punta)"/>')
partes.append(f'<path d="M{x(fin["8b."]):.1f} {y8b + 15}V{y_entrega - 2}H{x(ENTREGA) - 9:.1f}" stroke="{ROJO}" stroke-width="2" fill="none" marker-end="url(#punta)"/>')

y_hitos = Y0 + len(TAREAS) * FILA
partes.append(f'<line x1="20" y1="{y_hitos}" x2="{X0 + ANCHO}" y2="{y_hitos}" stroke="#e3e6ec"/>')
partes.append(texto(20, y_hitos + 27, "Hitos", font_weight=700))
for indice, (fecha, nombre) in enumerate(HITOS):
    px = x(fecha)
    partes.append(f'<path d="M{px:.1f} {y_hitos + 7}l7 8l-7 8l-7-8z" fill="#17233b"/>')
    # Las etiquetas alternan lado y línea para no pisarse: hay hitos muy cercanos
    derecha, linea = [(False, 19), (True, 52), (True, 19), (False, 36)][indice]
    partes.append(texto(px + (12 if derecha else -12), y_hitos + linea, nombre, text_anchor="start" if derecha else "end", font_size=11))

hoy = x(FECHA_INFORME)
partes.append(f'<line x1="{hoy:.1f}" y1="{Y0 - 4}" x2="{hoy:.1f}" y2="{Y0 + fondo}" stroke="#b3261e" stroke-width="2"/>')

y_ley = Y0 + fondo + 34
leyenda = [
    (20, '<rect x="20" y="{y}" width="34" height="9" fill="#a8afbc"/>', "Previsto en el protocolo"),
    (230, '<rect x="230" y="{y}" width="34" height="15" fill="#2f7d4f"/>', "Trabajado, tarea finalizada"),
    (470, '<rect x="470" y="{y}" width="34" height="15" fill="#2469a6"/>', "Trabajado, tarea abierta"),
    (690, '<rect x="690" y="{y}" width="34" height="15" fill="url(#rayas)" stroke="#c8641e"/>', "Reprogramado"),
    (850, '<rect x="850" y="{y}" width="34" height="15" fill="#eceef2"/>', "Pausa del proyecto"),
    (1030, '<line x1="1047" x2="1047" y1="{y}" y2="{y2}" stroke="#b3261e" stroke-width="2"/>', "Fecha del informe"),
    (1220, '<rect x="1220" y="{y}" width="34" height="15" fill="url(#rayas)" stroke="#b3261e" stroke-width="2.5"/>', "Camino crítico"),
]
for px, forma, etiqueta in leyenda:
    partes.append(forma.format(y=y_ley, y2=y_ley + 15))
    partes.append(texto(px + 42, y_ley + 13, etiqueta))
partes.append(texto(20, y_ley + 46, "Las barras de las tareas 1 a 5 anteriores a la fecha de inicio prevista (21/09) corresponden a la etapa de propuesta, encuesta y al backend inicial.", font_size=12))
partes.append(texto(20, y_ley + 66, f"Camino crítico: 7. Testing y despliegue → 8b. Memoria → Entrega final. Una demora en cualquiera de ellas corre la entrega; el margen es de {(ENTREGA - fin['8b.']).days} días.", font_size=12, fill=ROJO))
partes.append("</svg>")

Path(__file__).with_name("gantt.svg").write_text("\n".join(partes), encoding="utf-8")
