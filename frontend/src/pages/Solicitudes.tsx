import { useCallback, useEffect, useState } from 'react'
import { api, mensajeDe, type Solicitud } from '../api'
import { Cargando, claseBoton, claseCampo, claseEtiqueta, claseSecundario, claseTarjeta, Mensaje, Panel, Titulo, useInstituciones } from '../ui'

export default function Solicitudes() {
  const instituciones = useInstituciones()
  const [items, setItems] = useState<Solicitud[] | null>(null)
  const [error, setError] = useState('')
  const [duplicada, setDuplicada] = useState<Solicitud | null>(null)
  const [correcto, setCorrecto] = useState('')

  const cargar = useCallback(() => {
    api<Solicitud[]>('/api/instituciones/solicitudes').then(setItems).catch((e) => setError(mensajeDe(e)))
  }, [])

  useEffect(cargar, [cargar])

  async function resolver(s: Solicitud, resultado: 'aceptada' | 'duplicada' | 'rechazada', institucion_id?: number) {
    setError('')
    try {
      await api(`/api/instituciones/solicitudes/${s.id}/resolver`, 'POST', { resultado, institucion_id })
      setDuplicada(null)
      setCorrecto('')
      cargar()
    } catch (e) {
      setError(mensajeDe(e))
    }
  }

  const candidatos = duplicada ? instituciones.filter((i) => i.provincia === duplicada.provincia) : []

  return (
    <>
      <Titulo>Solicitudes</Titulo>
      <Mensaje>{error}</Mensaje>
      {items === null && !error && <Cargando />}
      {items?.length === 0 && <p className="py-8 text-center text-suave">No hay solicitudes pendientes.</p>}
      <div className="grid gap-3 md:grid-cols-2">
        {items?.map((s) => (
          <article key={s.id} className={`${claseTarjeta} flex flex-col gap-2 p-4`}>
            <h2 className="font-mano text-[28px] leading-[1.1]">{s.nombre}</h2>
            <p className="text-sm text-suave">{s.ciudad}, {s.provincia} · Para: {s.publicacion_titulo}</p>
            <div className="flex flex-wrap gap-2">
              <button type="button" className={`${claseSecundario} bg-menta! text-sm`} onClick={() => resolver(s, 'aceptada')}>Aceptar</button>
              <button type="button" className={`${claseSecundario} text-sm`} onClick={() => setDuplicada(s)}>Ya existe</button>
              <button type="button" className={`${claseSecundario} text-sm`} onClick={() => window.confirm(`¿Rechazar "${s.nombre}"? La publicación queda como borrador.`) && resolver(s, 'rechazada')}>No existe</button>
            </div>
          </article>
        ))}
      </div>
      <Panel abierto={duplicada !== null} cerrar={() => setDuplicada(null)} titulo="¿Cuál es el colegio?">
        <label className={claseEtiqueta}>
          Colegio correcto
          <select className={claseCampo} value={correcto} onChange={(e) => setCorrecto(e.target.value)}>
            <option value="">Elegí uno</option>
            {candidatos.map((i) => <option key={i.id} value={i.id}>{i.nombre} · {i.ciudad}</option>)}
          </select>
        </label>
        <button type="button" className={claseBoton} disabled={!correcto} onClick={() => resolver(duplicada!, 'duplicada', Number(correcto))}>Asignar y publicar</button>
      </Panel>
    </>
  )
}
