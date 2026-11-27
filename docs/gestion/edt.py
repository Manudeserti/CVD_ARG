"""Genera edt.svg. Las horas reales salen de docs/horas.csv; para actualizar estados, cambiar EDT y volver a correrlo."""
import csv
import textwrap
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape

AQUI = Path(__file__).parent
FECHA = "27/11/2026"

# número, nombre, horas del protocolo, estado, [(número, nombre, estado)]
EDT = [
    ("1", "Relevamiento y especificación", 20, "En revisión", [
        ("1.1", "Propuesta y encuesta", "Terminado"),
        ("1.2", "Protocolo", "Terminado"),
        ("1.3", "Requerimientos y reglas de negocio", "En revisión"),
        ("1.4", "Casos de uso", "En revisión"),
    ]),
    ("2", "Arquitectura, datos y UI/UX", 30, "En revisión", [
        ("2.1", "Elección del stack y de la plataforma de despliegue", "Terminado"),
        ("2.2", "Modelo del dominio y modelo de datos", "En revisión"),
        ("2.3", "Arquitectura en capas y despliegue", "En revisión"),
        ("2.4", "Diagramas de secuencia y de estados", "En revisión"),
        ("2.5", "Bocetos de interfaz y mapa de navegación", "En revisión"),
    ]),
    ("3", "Backend y API", 40, "Terminado", [
        ("3.1", "Estructura base (FastAPI y Supabase)", "Terminado"),
        ("3.2", "Registro y login con JWT", "Terminado"),
        ("3.3", "Instituciones y colegios a pedido", "Terminado"),
        ("3.4", "Publicaciones, catálogo con filtros y fotos", "Terminado"),
        ("3.5", "Auditoría y correcciones de seguridad", "Terminado"),
    ]),
    ("4", "Módulo transaccional", 25, "Terminado", [
        ("4.1", "Reservas, comisión y donaciones", "Terminado"),
        ("4.2", "Retención de fondos (decisión 002)", "Terminado"),
        ("4.3", "Integración con Mercado Pago (Checkout Pro y webhook)", "Terminado"),
        ("4.4", "Cancelaciones, devoluciones y vencimientos", "Terminado"),
    ]),
    ("5", "Validación QR", 20, "Terminado", [
        ("5.1", "Generación del código y liberación de fondos", "Terminado"),
        ("5.2", "QR del comprador y escaneo con la cámara", "Terminado"),
        ("5.3", "Actualización automática del estado", "Terminado"),
    ]),
    ("6", "Frontend responsive", 35, "Terminado", [
        ("6.1", "Catálogo, publicación, cuenta y operaciones", "Terminado"),
        ("6.2", "Diseño para celular, tablet y PC, y logo", "Terminado"),
        ("6.3", "Localidades oficiales y buscador de colegios", "Terminado"),
        ("6.4", "Panel de solicitudes de colegios", "Terminado"),
    ]),
    ("7", "Testing y despliegue", 20, "En curso", [
        ("7.1", "Plan de pruebas (CP-01 a CP-36)", "En curso"),
        ("7.2", "Tests automáticos de la API", "En curso"),
        ("7.3", "Prueba de punta a punta en navegador", "Terminado"),
        ("7.4", "Pruebas con Mercado Pago y celulares reales", "Terminado"),
        ("7.5", "Medición de rendimiento y prueba con usuarios", "Pendiente"),
        ("7.6", "Despliegue en Vercel y Supabase", "Terminado"),
    ]),
    ("8", "Memoria y manuales", 10, "En curso", [
        ("8.1", "Marco teórico y estado del arte", "En curso"),
        ("8.2", "Capítulos de la memoria", "En curso"),
        ("8.3", "Manual técnico", "En curso"),
        ("8.4", "Manual de usuario", "Pendiente"),
        ("8.5", "Informes de avance y Gantt", "En curso"),
        ("8.6", "Registro de horas, uso de IA y bitácora", "En curso"),
        ("8.7", "Indicadores de retrabajo de la IA", "Pendiente"),
    ]),
]

# borde, relleno
COLOR = {
    "Terminado": ("#2f7d4f", "#e6f2ea"),
    "En revisión": ("#c8641e", "#fbede3"),
    "En curso": ("#2469a6", "#e4eef7"),
    "Pendiente": ("#8a8f98", "#f1f2f4"),
}
COL, GAP, M = 214, 14, 20
ANCHO = M * 2 + COL * len(EDT) + GAP * (len(EDT) - 1)
LINEA = 15


def horas_reales():
    total = defaultdict(float)
    with open(AQUI.parent / "horas.csv", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            total[fila["actividad"].split(" ")[0]] += float(fila["horas"])
    return total


def caja(x, y, ancho, lineas, estado, negrita=False, centrado=False):
    borde, relleno = COLOR[estado]
    alto = 12 + LINEA * len(lineas)
    partes = [f'<rect x="{x}" y="{y}" width="{ancho}" height="{alto}" rx="4" fill="{relleno}" stroke="{borde}" stroke-width="1.5"/>']
    tx, ancla = (x + ancho / 2, "middle") if centrado else (x + 8, "start")
    for i, linea in enumerate(lineas):
        peso = ' font-weight="700"' if negrita and i < len(lineas) - 1 else ""  # la última línea son las horas
        partes.append(f'<text x="{tx}" y="{y + 18 + i * LINEA}" text-anchor="{ancla}"{peso}>{escape(linea)}</text>')
    return partes, alto


def fmt(horas):
    return f"{horas:.1f}".replace(".", ",")


reales = horas_reales()
partes = []
y_raiz = 70
raiz, alto_raiz = caja(ANCHO / 2 - 170, y_raiz, 340, ["CVD: plataforma de compra, venta y donación", f"Protocolo: 200 h · Real al {FECHA}: {fmt(sum(reales.values()))} h"], "En curso", centrado=True)
partes += raiz
y_bus = y_raiz + alto_raiz + 18
y_n1 = y_bus + 18
partes.append(f'<line x1="{M + COL / 2}" y1="{y_bus}" x2="{ANCHO - M - COL / 2}" y2="{y_bus}" stroke="#17233b"/>')
partes.append(f'<line x1="{ANCHO / 2}" y1="{y_raiz + alto_raiz}" x2="{ANCHO / 2}" y2="{y_bus}" stroke="#17233b"/>')

fondo = 0
for i, (numero, nombre, previstas, estado, hijos) in enumerate(EDT):
    x = M + i * (COL + GAP)
    partes.append(f'<line x1="{x + COL / 2}" y1="{y_bus}" x2="{x + COL / 2}" y2="{y_n1}" stroke="#17233b"/>')
    lineas = textwrap.wrap(f"{numero}. {nombre}", 28) + [f"Prev. {previstas} h · Real {fmt(reales[numero])} h"]
    bloque, alto = caja(x, y_n1, COL, lineas, estado, negrita=True)
    partes += bloque
    y = y_n1 + alto + 12
    x_tronco = x + 12
    for sub, sub_nombre, sub_estado in hijos:
        bloque, alto_hijo = caja(x + 24, y, COL - 24, textwrap.wrap(f"{sub} {sub_nombre}", 26), sub_estado)
        partes += bloque
        partes.append(f'<line x1="{x_tronco}" y1="{y + alto_hijo / 2}" x2="{x + 24}" y2="{y + alto_hijo / 2}" stroke="#17233b"/>')
        y_ultimo = y + alto_hijo / 2
        y += alto_hijo + 8
    partes.append(f'<line x1="{x_tronco}" y1="{y_n1 + alto}" x2="{x_tronco}" y2="{y_ultimo}" stroke="#17233b"/>')
    fondo = max(fondo, y)

y_ley = fondo + 22
x_ley = M
leyenda = []
for estado, (borde, relleno) in COLOR.items():
    leyenda.append(f'<rect x="{x_ley}" y="{y_ley}" width="26" height="14" rx="3" fill="{relleno}" stroke="{borde}" stroke-width="1.5"/>')
    leyenda.append(f'<text x="{x_ley + 34}" y="{y_ley + 12}">{estado}</text>')
    x_ley += 150
alto_total = y_ley + 40

svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ANCHO} {alto_total}" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#17233b">',
    f'<rect width="{ANCHO}" height="{alto_total}" fill="#fff"/>',
    f'<text x="{M}" y="32" font-size="20" font-weight="700">Trabajo Final CVD: estructura de desglose del trabajo (EDT)</text>',
    f'<text x="{M}" y="52">Situación al {FECHA}. Primer nivel: las 8 tareas del protocolo y del Gantt. Responsable de todos los paquetes: Manuel Deserti.</text>',
    *partes,
    *leyenda,
    "</svg>",
]
(AQUI / "edt.svg").write_text("\n".join(svg), encoding="utf-8")
print(f"edt.svg: {ANCHO}x{alto_total}")
