# Genera los checklists de los informes de avance.
# Requiere python-docx. Uso: python checklists.py <carpeta de salida> <gantt.png>
import sys
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

SALIDA = sys.argv[1]
T, P, N = 0, 1, 2

CAUSA = "El trabajo se pausó entre el 22/08 y el 02/11/2026 porque estaba en pleno desarrollo de otro proyecto (hot-ar). Al retomar prioricé la implementación."

def j(hecho, pendiente, causa, efecto, accion, fecha):
    return [("Realizado: ", hecho), ("Pendiente: ", pendiente), ("Causa: ", causa), ("Efecto: ", efecto), ("Acción correctiva: ", accion), ("Nueva fecha: ", fecha)]

GANTT = ("Nuevo diagrama de Gantt actualizado presentado", T, None)

PRIMERO = [
    ("Introducción", P, j(
        "borrador con contexto, motivación, problema y alcance, basado en el protocolo y la encuesta.",
        "versión final con las correcciones del director.",
        CAUSA, "no afecta otras tareas ni la fecha de entrega.",
        "reescribir el borrador e incorporar las observaciones del director.", "26/11/2026.")),
    ("Objetivos", P, j(
        "objetivo general definido en el protocolo y borrador de ocho objetivos específicos.",
        "validar los objetivos específicos con el director.",
        CAUSA, "los requerimientos ya están vinculados a esta propuesta y podrían ajustarse.",
        "ajustarlos con las observaciones del director.", "26/11/2026.")),
    ("Marco teórico o estado del arte", P, j(
        "comparación con soluciones existentes (Colmena Escolar y ScoolApp) en el protocolo, encuesta con 381 respuestas, relevamiento normativo de la retención de fondos (BCRA, UIF, Ley 24.240) y documentación técnica oficial de Mercado Pago. Las decisiones técnicas se registraron con las alternativas evaluadas, y el diseño sigue la notación UML de Larman.",
        "falta la bibliografía académica y la redacción de las dos secciones con citas en APA 7. Marco teórico: economía circular, mercados entre particulares y confianza, retención de fondos, pasarelas de pago, códigos QR y seguridad de la API. Estado del arte: ampliar la comparación con otras alternativas (grupos de WhatsApp, Marketplace, plataformas de ropa usada) en una tabla con tecnología, limitaciones y diferencial.",
        CAUSA, "no demora la implementación, ya avanzada. La bibliografía se usa para fundamentar las decisiones registradas y, si alguna fuente lo indica, revisarlas.",
        "seleccionar y leer las fuentes desde el 18/11, vincular cada concepto con el diseño, la implementación y las pruebas, y revisar el avance con el director.", "30/11/2026.")),
    ("Metodología", P, j(
        "borrador con las metodologías de relevamiento, desarrollo y validación.",
        "versión final con las correcciones del director.",
        CAUSA, "no afecta otras tareas ni la fecha de entrega.",
        "reescribir el borrador e incorporar las observaciones del director.", "26/11/2026.")),
    ("Requerimientos preliminares", T, None),
    GANTT,
]

SEGUNDO = [
    ("Requerimientos completos", P, j(
        "requerimientos funcionales y no funcionales, reglas de negocio, restricciones, diagrama de casos de uso y especificación en formato completo de los casos principales, según la notación de Larman.",
        "validación con el director y definición de la meta de tiempo de respuesta (RNF-10).",
        CAUSA + " Los requerimientos ya estaban definidos en el protocolo y en la encuesta; su formalización en casos de uso se completó después del código.",
        "no afecta la implementación ni la fecha de entrega.",
        "incorporar las observaciones del director.", "26/11/2026.")),
    ("Diseño del sistema", P, j(
        "arquitectura en capas, diagramas de despliegue (con componentes) y de paquetes, modelo del dominio, modelo de datos, diagramas de estados (incluida la navegación) y de secuencia, seguridad y patrones. Los diagramas se rehicieron según la notación UML de Larman.",
        "validación con el director y definir si se agrega un diagrama de clases de diseño.",
        CAUSA + " Las decisiones de diseño se tomaron al implementar, evaluando alternativas, y quedaron registradas; los diagramas UML se formalizaron después.",
        "no afecta la implementación ni la fecha de entrega.",
        "incorporar las observaciones del director.", "26/11/2026.")),
    ("Implementación", T, None),
    ("Plan de pruebas", P, j(
        "estrategia, tipos de prueba, entornos, criterios de aceptación, 36 casos de prueba y matriz de trazabilidad con los requerimientos. Hay pruebas automáticas de API y de punta a punta, y verificaciones manuales de pago y escaneo.",
        "tres casos automáticos por agregar (CP-32 a CP-34), medición de tiempos (CP-35) y prueba con usuarios (CP-36).",
        CAUSA, "se acorta el tiempo disponible para la validación, sin mover la fecha de entrega.",
        "completar los casos pendientes y acordar con el director el alcance de la prueba con usuarios.", "05/12/2026.")),
    GANTT,
]

COLUMNAS = ["Ítem solicitado", "Cumplido totalmente", "Cumplido parcialmente", "Muy demorado o no cumplido", "Justificación, acción correctiva y nueva fecha"]
ANCHOS = [Cm(4.2), Cm(1.9), Cm(1.9), Cm(2.0), Cm(15.7)]

def sombra(celda, color="E8ECF2"):
    s = OxmlElement("w:shd"); s.set(qn("w:val"), "clear"); s.set(qn("w:color"), "auto"); s.set(qn("w:fill"), color)
    celda._tc.get_or_add_tcPr().append(s)

def poner(celda, texto, negrita=False, centrado=False):
    p = celda.paragraphs[0]; r = p.add_run(texto); r.bold = negrita
    if centrado: p.alignment = WD_ALIGN_PARAGRAPH.CENTER

def generar(titulo, nota, filas, archivo):
    doc = Document()
    estilo = doc.styles["Normal"]; estilo.font.name = "Arial"; estilo.font.size = Pt(10)
    s = doc.sections[0]
    s.orientation = WD_ORIENT.LANDSCAPE; s.page_width, s.page_height = Cm(29.7), Cm(21)
    s.left_margin = s.right_margin = Cm(2); s.top_margin = s.bottom_margin = Cm(1.8)

    p = doc.add_paragraph(); r = p.add_run("UNMDP · Facultad de Ingeniería · Ingeniería en Informática"); r.font.size = Pt(9)
    p = doc.add_paragraph(); r = p.add_run(titulo); r.bold = True; r.font.size = Pt(15)
    doc.add_paragraph("Plataforma web de economía escolar circular con mecanismo de validación de transacciones")
    if nota:
        doc.add_paragraph(nota)

    datos = doc.add_table(rows=2, cols=5); datos.style = "Table Grid"
    for i, (t, v) in enumerate([
        ("Estudiante", "Manuel Deserti"), ("Director", "Cristian Ariel Remon"), ("Codirector", "No tiene"),
        ("Tipo de TF", "Tipo 1: Proyecto de Ingeniería"), ("Fecha", "__/__/2026"),
    ]):
        poner(datos.cell(0, i), t, negrita=True); sombra(datos.cell(0, i)); poner(datos.cell(1, i), v)
    doc.add_paragraph()

    tabla = doc.add_table(rows=1, cols=5); tabla.style = "Table Grid"; tabla.autofit = False
    for i, c in enumerate(COLUMNAS):
        poner(tabla.rows[0].cells[i], c, negrita=True, centrado=0 < i < 4); sombra(tabla.rows[0].cells[i])
    for item, estado, justificacion in filas:
        celdas = tabla.add_row().cells
        poner(celdas[0], item, negrita=True)
        poner(celdas[1 + estado], "X", negrita=True, centrado=True)
        if justificacion:
            for n, (rotulo, texto) in enumerate(justificacion):
                p = celdas[4].paragraphs[0] if n == 0 else celdas[4].add_paragraph()
                p.paragraph_format.space_after = Pt(2)
                p.add_run(rotulo).bold = True; p.add_run(texto)
    for fila in tabla.rows:
        for i, ancho in enumerate(ANCHOS):
            fila.cells[i].width = ancho

    doc.add_page_break()
    p = doc.add_paragraph(); r = p.add_run("Diagrama de Gantt actualizado"); r.bold = True; r.font.size = Pt(13)
    doc.add_picture(sys.argv[2], width=Cm(25.6))
    doc.add_paragraph("Documento de autoevaluación y seguimiento del Trabajo Final")
    doc.save(f"{SALIDA}/{archivo}")

generar("Checklist del Primer Informe de Avance",
        "Este informe estaba previsto para el 14/10/2026 en el protocolo y se presenta fuera de término, por la pausa del proyecto indicada abajo.",
        PRIMERO, "primer-informe-de-avance.docx")
generar("Checklist del Segundo Informe de Avance", None, SEGUNDO, "segundo-informe-de-avance.docx")

for a in ("primer-informe-de-avance.docx", "segundo-informe-de-avance.docx"):
    d = Document(f"{SALIDA}/{a}")
    t = d.tables[1]
    print(a, len(t.rows), "filas;", [sum(c.text == "X" for c in [f.cells[i] for f in t.rows]) for i in (1, 2, 3)], "imagenes", len(d.inline_shapes))
