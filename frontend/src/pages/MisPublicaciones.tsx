import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, mensajeDe, type EstadoPublicacion, type Publicacion } from '../api'
import { useSesion } from '../sesion'
import { Cargando, claseBoton, claseSecundario, Mensaje, Panel, precioTexto, SelectorColegio, TarjetaArticulo, Titulo, detalleDe, useInstituciones } from '../ui'

const ESTADOS: Record<EstadoPublicacion, string> = {
  disponible: 'Publicada',
  reservado: 'Reservada',
  vendido: 'Entregada',
  baja: 'Dada de baja',
  pendiente_colegio: 'Esperando el alta del colegio',
  borrador: 'Borrador',
}
const SE_PUEDE_DAR_DE_BAJA: EstadoPublicacion[] = ['disponible', 'pendiente_colegio', 'borrador']

export default function MisPublicaciones() {
  const { usuario } = useSesion()
  const instituciones = useInstituciones()
  const [items, setItems] = useState<Publicacion[] | null>(null)
  const [error, setError] = useState('')
  const [editando, setEditando] = useState<Publicacion | null>(null)
  const [ciudad, setCiudad] = useState('')
  const [colegio, setColegio] = useState<number | null>(null)

  const cargar = useCallback(() => {
    api<Publicacion[]>('/api/publicaciones/mias').then(setItems).catch((e) => setError(mensajeDe(e)))
  }, [])

  useEffect(cargar, [cargar])

  async function darDeBaja(p: Publicacion) {
    if (!window.confirm(`¿Dar de baja "${p.titulo}"?`)) return
    setError('')
    try {
      await api(`/api/publicaciones/${p.id}`, 'DELETE')
      cargar()
    } catch (e) {
      setError(mensajeDe(e))
    }
  }

  async function publicarConColegio() {
    setError('')
    try {
      await api(`/api/publicaciones/${editando!.id}/institucion`, 'PUT', { institucion_id: colegio })
      setEditando(null)
      setColegio(null)
      setCiudad('')
      cargar()
    } catch (e) {
      setError(mensajeDe(e))
      setEditando(null)
    }
  }

  return (
    <>
      <div className="flex items-center justify-between">
        <Titulo>Mis artículos</Titulo>
        {usuario?.rol === 'admin' && <Link to="/admin/solicitudes" className={`${claseSecundario} text-sm`}>Solicitudes</Link>}
      </div>
      <Mensaje>{error}</Mensaje>
      {items === null && !error && <Cargando />}
      {items?.length === 0 && <p className="py-8 text-center text-suave">Todavía no publicaste nada.</p>}
      <div className="grid gap-3 md:grid-cols-2">
        {items?.map((p, i) => (
          <article key={p.id} className="flex flex-col gap-2">
            <TarjetaArticulo titulo={p.titulo} detalle={detalleDe(p, instituciones)} precio={precioTexto(p.tipo, p.precio)} foto={p.imagenes_urls[0]} indice={i} />
            <div className="flex flex-wrap items-center gap-2 px-1">
              <span className="text-[13px] font-semibold">{ESTADOS[p.estado]}</span>
              <span className="ml-auto flex gap-2">
                {p.estado === 'borrador' && <button type="button" className={`${claseSecundario} text-sm`} onClick={() => setEditando(p)}>Elegir colegio</button>}
                {SE_PUEDE_DAR_DE_BAJA.includes(p.estado) && <button type="button" className={`${claseSecundario} text-sm`} onClick={() => darDeBaja(p)}>Dar de baja</button>}
              </span>
            </div>
            {p.aviso && <Mensaje tipo="info">{p.aviso}</Mensaje>}
          </article>
        ))}
      </div>
      <Panel abierto={editando !== null} cerrar={() => setEditando(null)} titulo="Elegí el colegio">
        <SelectorColegio instituciones={instituciones} ciudad={ciudad} setCiudad={(c) => { setCiudad(c); setColegio(null) }} colegio={colegio} setColegio={setColegio} />
        <button type="button" className={claseBoton} disabled={colegio === null} onClick={publicarConColegio}>Publicar</button>
      </Panel>
    </>
  )
}
