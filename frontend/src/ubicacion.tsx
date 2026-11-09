import { useEffect, useId, useState } from 'react'
import type { Institucion } from './api'
import { claseCampo, claseEtiqueta } from './ui'

export interface Ubicacion {
  provincia: string
  ciudad: string
  institucion_id: string
}

export interface Lugar {
  provincia: string
  ciudad: string
}

const CLAVE = 'cvd_ubicacion'
export const SIN_UBICACION: Ubicacion = { provincia: '', ciudad: '', institucion_id: '' }
export const SIN_LUGAR: Lugar = { provincia: '', ciudad: '' }

export function leerUbicacion(): Ubicacion {
  const guardada = localStorage.getItem(CLAVE)
  return guardada ? (JSON.parse(guardada) as Ubicacion) : SIN_UBICACION
}

export function guardarUbicacion(u: Ubicacion) {
  localStorage.setItem(CLAVE, JSON.stringify(u))
}

export function nombreUbicacion(u: Ubicacion, instituciones: Institucion[]) {
  return instituciones.find((i) => String(i.id) === u.institucion_id)?.nombre || u.ciudad || u.provincia || 'Todo el país'
}

type Localidades = Record<string, string[]>
let carga: Promise<Localidades> | undefined

/** Provincias y localidades oficiales (Georef). Se generan con scripts/localidades.mjs. */
function useLocalidades() {
  const [localidades, setLocalidades] = useState<Localidades>({})
  useEffect(() => {
    carga ??= fetch('/localidades.json').then((r) => r.json())
    carga.then(setLocalidades).catch(() => setLocalidades({}))
  }, [])
  return localidades
}

const unicos = (valores: string[]) => [...new Set(valores)].sort((a, b) => a.localeCompare(b, 'es'))
const normal = (s: string) => s.normalize('NFD').replace(/\p{M}/gu, '').trim().toLowerCase()

/** Con `libre` acepta lo que no esté en la lista, para que nadie quede afuera si al dataset le falta su localidad. */
function CampoLocalidad({ opciones, deshabilitado, valor, cambiar, libre = false }: {
  opciones: string[]
  deshabilitado: boolean
  valor: string
  cambiar: (ciudad: string) => void
  libre?: boolean
}) {
  const lista = useId()
  const [texto, setTexto] = useState(valor)

  function escribir(t: string) {
    const exacta = opciones.find((o) => normal(o) === normal(t))
    setTexto(exacta ?? t)
    cambiar(exacta ?? (libre ? t : ''))
  }

  return (
    <label className={claseEtiqueta}>
      Localidad
      <input className={claseCampo} list={lista} value={texto} disabled={deshabilitado} required={libre} placeholder={deshabilitado ? 'Primero elegí la provincia' : 'Escribí para buscar'} onChange={(e) => escribir(e.target.value)} autoComplete="off" />
      <datalist id={lista}>{opciones.map((o) => <option key={o} value={o} />)}</datalist>
    </label>
  )
}

/** Provincia, después localidad, después colegio: cada paso se llena según el anterior. */
export function SelectorUbicacion({ instituciones, valor, cambiar }: { instituciones: Institucion[]; valor: Ubicacion; cambiar: (u: Ubicacion) => void }) {
  const localidades = useLocalidades()
  const enProvincia = instituciones.filter((i) => i.provincia === valor.provincia)
  const colegios = enProvincia.filter((i) => i.ciudad === valor.ciudad)
  return (
    <>
      <label className={claseEtiqueta}>
        Provincia
        <select className={claseCampo} value={valor.provincia} onChange={(e) => cambiar({ provincia: e.target.value, ciudad: '', institucion_id: '' })}>
          <option value="">Todas</option>
          {Object.keys(localidades).map((p) => <option key={p}>{p}</option>)}
        </select>
      </label>
      {/* Suma las ciudades de los colegios: un alta pudo traer una localidad que el dataset no tiene */}
      <CampoLocalidad
        key={valor.provincia}
        opciones={unicos([...(localidades[valor.provincia] ?? []), ...enProvincia.map((i) => i.ciudad)])}
        deshabilitado={!valor.provincia}
        valor={valor.ciudad}
        cambiar={(ciudad) => cambiar({ ...valor, ciudad, institucion_id: '' })}
      />
      <label className={claseEtiqueta}>
        Colegio
        <select className={claseCampo} value={valor.institucion_id} disabled={colegios.length === 0} onChange={(e) => cambiar({ ...valor, institucion_id: e.target.value })}>
          <option value="">Todos</option>
          {colegios.map((i) => <option key={i.id} value={i.id}>{i.nombre}</option>)}
        </select>
        {valor.ciudad && colegios.length === 0 && <span className="font-normal text-suave">Todavía no hay colegios cargados en {valor.ciudad}.</span>}
      </label>
    </>
  )
}

/** Para publicar: provincia, localidad y los colegios de ese lugar. */
export function SelectorColegio({ instituciones, lugar, setLugar, colegio, setColegio }: {
  instituciones: Institucion[]
  lugar: Lugar
  setLugar: (l: Lugar) => void
  colegio: number | null
  setColegio: (id: number) => void
}) {
  const localidades = useLocalidades()
  const [busqueda, setBusqueda] = useState('')
  const delLugar = instituciones.filter((i) => i.provincia === lugar.provincia && normal(i.ciudad) === normal(lugar.ciudad))
  // El elegido sigue a la vista aunque la búsqueda ya no lo incluya
  const visibles = delLugar.filter((i) => i.id === colegio || normal(i.nombre).includes(normal(busqueda)))

  function cambiarLugar(l: Lugar) {
    setBusqueda('')
    setLugar(l)
  }

  return (
    <>
      <label className={claseEtiqueta}>
        Provincia
        <select className={claseCampo} required value={lugar.provincia} onChange={(e) => cambiarLugar({ provincia: e.target.value, ciudad: '' })}>
          <option value="">Elegí una</option>
          {Object.keys(localidades).map((p) => <option key={p}>{p}</option>)}
        </select>
      </label>
      <CampoLocalidad key={lugar.provincia} libre opciones={localidades[lugar.provincia] ?? []} deshabilitado={!lugar.provincia} valor={lugar.ciudad} cambiar={(ciudad) => cambiarLugar({ ...lugar, ciudad })} />
      {delLugar.length > 0 && (
        <fieldset className="flex flex-col gap-1.5">
          <legend className="mb-1 text-[13px] font-medium">Colegio</legend>
          {/* Enter no tiene que enviar el formulario de publicación */}
          <input type="search" className={claseCampo} aria-label="Buscar colegio" placeholder="Buscar colegio" value={busqueda} onChange={(e) => setBusqueda(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && e.preventDefault()} autoComplete="off" />
          {visibles.length === 0 && <p className="px-1 text-sm text-suave">No encontramos ese colegio en {lugar.ciudad}.</p>}
          <div className="max-h-60 overflow-y-auto rounded-2xl border border-linea bg-white empty:hidden">
            {visibles.map((i) => (
              <label key={i.id} className={`flex min-h-12 items-center gap-2.5 border-b border-linea px-3.5 last:border-b-0 ${colegio === i.id ? 'bg-amarillo/40 font-semibold' : ''}`}>
                <input type="radio" name="colegio" className="size-[18px] accent-tinta" checked={colegio === i.id} onChange={() => setColegio(i.id)} />
                {i.nombre}
              </label>
            ))}
          </div>
        </fieldset>
      )}
    </>
  )
}
