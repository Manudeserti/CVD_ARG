// Imprime a PDF los HTML de pdf_html.py con el Chrome instalado.
// Uso: node docs/gestion/html_pdf.mjs <ruta absoluta a frontend> "<html>|<pdf>|<horizontal 0/1>|<texto del pie>" ...
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
const [fe, ...pares] = process.argv.slice(2)
const { chromium } = createRequire(fe + '/package.json')('playwright-core')
const b = await chromium.launch({ channel: 'chrome', headless: true })
const p = await b.newPage()
for (const par of pares) {
  const [html, pdf, horizontal, pie] = par.split('|')
  await p.goto(pathToFileURL(html).href, { waitUntil: 'load' })
  await p.pdf({
    path: pdf, format: 'A4', landscape: horizontal === '1', printBackground: true,
    margin: { top: '15mm', bottom: '18mm', left: '18mm', right: '18mm' },
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: `<div style="font: 8pt Cambria, serif; color:#555; width:100%; padding:0 18mm; display:flex; justify-content:space-between"><span>${pie}</span><span>Página <span class="pageNumber"></span> de <span class="totalPages"></span></span></div>`,
  })
}
await b.close()
