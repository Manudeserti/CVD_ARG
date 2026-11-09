// Genera public/localidades.json desde Georef, la API oficial de localidades de Argentina.
// Se corre a mano desde frontend/ cuando se quiera actualizar: node scripts/localidades.mjs
import { writeFileSync } from 'node:fs'

const URL_GEOREF = 'https://apis.datos.gob.ar/georef/api/localidades?campos=nombre,provincia.nombre&max=5000'
// Los mismos nombres cortos que ya se guardan en la base
const CORTOS = {
  'Ciudad Autónoma de Buenos Aires': 'CABA',
  'Tierra del Fuego, Antártida e Islas del Atlántico Sur': 'Tierra del Fuego',
}
const orden = (a, b) => a.localeCompare(b, 'es')

const respuesta = await fetch(URL_GEOREF)
if (!respuesta.ok) throw new Error(`Georef respondió ${respuesta.status}`)
const { total, localidades } = await respuesta.json()
if (total !== localidades.length) throw new Error(`Llegaron ${localidades.length} de ${total} localidades`)

const porProvincia = {}
for (const { nombre, provincia } of localidades) {
  ;(porProvincia[CORTOS[provincia.nombre] ?? provincia.nombre] ??= new Set()).add(nombre)
}

const salida = Object.fromEntries(
  Object.keys(porProvincia).sort(orden).map((p) => [p, [...porProvincia[p]].sort(orden)]),
)
writeFileSync(new URL('../public/localidades.json', import.meta.url), JSON.stringify(salida))
console.log(`${Object.keys(salida).length} provincias, ${Object.values(salida).flat().length} localidades`)
