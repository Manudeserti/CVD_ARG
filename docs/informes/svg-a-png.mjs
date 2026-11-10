// Convierte SVG a PNG con el Chrome instalado.
// Uso: node svg-a-png.mjs <ruta absoluta a frontend> "<svg>|<png>|<ancho>|<alto>|<escala>"
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
const [fe, ...pares] = process.argv.slice(2)
const require = createRequire(fe + '/package.json')
const { chromium } = require('playwright-core')
const b = await chromium.launch({ channel: 'chrome', headless: true })
for (const par of pares) {
  const [svg, png, w, h, escala] = par.split('|')
  const ctx = await b.newContext({ viewport: { width: +w, height: +h }, deviceScaleFactor: +(escala || 1) })
  const p = await ctx.newPage()
  await p.goto(pathToFileURL(svg).href)
  await p.screenshot({ path: png })
}
await b.close()
