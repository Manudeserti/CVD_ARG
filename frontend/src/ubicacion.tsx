import type { Institucion } from './api'
import { claseCampo, claseEtiqueta, unicos } from './ui'

export interface Ubicacion {
  provincia: string
  ciudad: string
  institucion_id: string
}

const CLAVE = 'cvd_ubicacion'
export const SIN_UBICACION: Ubicacion = { provincia: '', ciudad: '', institucion_id: '' }

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

/** Provincia, después ciudad, después colegio: cada paso se llena según el anterior. */
export function SelectorUbicacion({ instituciones, valor, cambiar }: { instituciones: Institucion[]; valor: Ubicacion; cambiar: (u: Ubicacion) => void }) {
  const enProvincia = instituciones.filter((i) => !valor.provincia || i.provincia === valor.provincia)
  const colegios = enProvincia.filter((i) => i.ciudad === valor.ciudad)
  return (
    <>
      <label className={claseEtiqueta}>
        Provincia
        <select className={claseCampo} value={valor.provincia} onChange={(e) => cambiar({ provincia: e.target.value, ciudad: '', institucion_id: '' })}>
          <option value="">Todas</option>
          {unicos(instituciones.map((i) => i.provincia)).map((p) => <option key={p}>{p}</option>)}
        </select>
      </label>
      <label className={claseEtiqueta}>
        Ciudad
        <select className={claseCampo} value={valor.ciudad} disabled={!valor.provincia} onChange={(e) => cambiar({ ...valor, ciudad: e.target.value, institucion_id: '' })}>
          <option value="">Todas</option>
          {unicos(enProvincia.map((i) => i.ciudad)).map((c) => <option key={c}>{c}</option>)}
        </select>
      </label>
      <label className={claseEtiqueta}>
        Colegio
        <select className={claseCampo} value={valor.institucion_id} disabled={!valor.ciudad} onChange={(e) => cambiar({ ...valor, institucion_id: e.target.value })}>
          <option value="">Todos</option>
          {colegios.map((i) => <option key={i.id} value={i.id}>{i.nombre}</option>)}
        </select>
      </label>
    </>
  )
}
