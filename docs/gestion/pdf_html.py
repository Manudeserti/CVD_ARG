"""Arma el HTML de la EDT y la bitácora para imprimir a PDF (requiere el paquete markdown).
Uso: python docs/gestion/pdf_html.py <repo> <carpeta de salida>; después node docs/gestion/html_pdf.mjs."""
import html as h, re, sys, pathlib, markdown

repo, salida = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
gestion = repo / "docs" / "gestion"
FECHA = "27/11/2026"

CSS = """

body { font-family: Cambria, 'Times New Roman', serif; font-size: 10.5pt; line-height: 1.35; color: #111; }
.portada { border-bottom: 1.5px solid #222; padding-bottom: 6pt; margin-bottom: 12pt; }
.inst { font-size: 9pt; letter-spacing: .5pt; text-transform: uppercase; color: #333; }
.titulo { font-size: 17pt; font-weight: bold; margin: 6pt 0 2pt; }
.sub { font-size: 10.5pt; }
.datos { font-size: 9.5pt; color: #333; margin-top: 4pt; }
h2 { font-size: 12pt; margin: 14pt 0 6pt; break-after: avoid; } h2 + ul { break-before: avoid; }
p { margin: 0 0 6pt; text-align: justify; }
table { border-collapse: collapse; width: 100%; }
td, th { border: 0.75px solid #777; padding: 3pt 6pt; vertical-align: top; text-align: left; }
tr { break-inside: avoid; }
.entrada { margin-bottom: 10pt; break-inside: avoid; }
.entrada th { background: #e6e9ee; font-size: 10.5pt; }
.entrada th span { float: right; font-weight: normal; }
.entrada td.campo { width: 23%; font-weight: bold; background: #f6f7f9; }
ol { margin: 0; padding-left: 15pt; } li { margin: 1pt 0; }
.dicc { font-size: 9pt; } .dicc th { background: #e6e9ee; } .dicc td:last-child { white-space: nowrap; }
ul { padding-left: 14pt; } img { width: 100%; }
"""


def portada(titulo):
    return (f'<div class="portada"><div class="inst">Universidad Nacional de Mar del Plata · Facultad de Ingeniería · Trabajo Final</div>'
            f'<div class="titulo">{titulo}</div><div class="sub">CVD: plataforma de compra, venta y donación</div>'
            f'<div class="datos">Autor: Manuel Deserti · Director: Cristian Remón · Situación al {FECHA}</div></div>')


def inline(t):
    t = re.sub(r"(?<!!)\[([^\]]+)\]\([^)]+\)", r"\1", t)  # sin links: apuntarían a archivos del repo
    t = h.escape(t.replace("`", ""), quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return re.sub(r"\*(.+?)\*", r"<i>\1</i>", t)


def pagina(titulo, cuerpo):
    return f'<!doctype html><meta charset="utf-8"><title>{titulo}</title><style>{CSS}</style>{portada(titulo)}{cuerpo}'


# Bitácora: cada entrada "## fecha · horas" con campos "- **Campo:** texto" y sublistas "  1. ..."
entradas, actual = [], None
for linea in (gestion / "bitacora.md").read_text(encoding="utf-8").splitlines():
    if linea.startswith("## "):
        fecha, _, horas = linea[3:].strip().partition(" · ")
        actual = {"fecha": fecha, "horas": horas, "campos": []}
        entradas.append(actual)
    elif actual and (m := re.match(r"- \*\*(.+?):\*\*\s*(.*)", linea)):
        actual["campos"].append([m[1], m[2].strip(), []])
    elif actual and actual["campos"] and (m := re.match(r"\s+\d+\.\s+(.*)", linea)):
        actual["campos"][-1][2].append(m[1])

cuerpo = ""
for e in entradas:
    filas = "".join(
        f'<tr><td class="campo">{campo}</td><td>{inline(texto)}'
        + (f'<ol>{"".join(f"<li>{inline(i)}</li>" for i in items)}</ol>' if items else "") + "</td></tr>"
        for campo, texto, items in e["campos"])
    cuerpo += f'<table class="entrada"><thead><tr><th colspan="2">{e["fecha"]}<span>{e["horas"]}</span></th></tr></thead>{filas}</table>'
(salida / "bitacora.html").write_text(pagina("Bitácora técnica de desarrollo", cuerpo), encoding="utf-8")

# EDT: página 1 introducción y observaciones; página 2 el diagrama solo; después el diccionario
md = (gestion / "edt.md").read_text(encoding="utf-8")
md = "\n".join(l for l in md.splitlines() if not l.startswith(("# ", "Situación al", "El diagrama se genera con", "![EDT]")))
md = re.sub(r"(?<!!)\[([^\]]+)\]\([^)]+\)", r"\1", md).replace("`", "")
intro, _, resto = md.partition("## Diccionario de la EDT")
dicc, _, obs = resto.partition("## Observaciones")
a_html = lambda t: markdown.markdown(t, extensions=["tables"])
diagrama = f'<img src="{(gestion / "edt.png").as_uri()}" style="display:block; margin:0 auto; width:auto; max-width:100%; max-height:172mm">'
cuerpo = (a_html(intro) + "<h2>Observaciones</h2>" + a_html(obs)
          + f'<div style="break-before: page">{diagrama}</div>'
          + '<h2 style="break-before: page">Diccionario de la EDT</h2>' + a_html(dicc).replace("<table>", '<table class="dicc">'))
(salida / "edt.html").write_text(pagina("Estructura de desglose del trabajo (EDT)", cuerpo), encoding="utf-8")
print(len(entradas), "entradas")
