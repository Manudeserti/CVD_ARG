import { useEffect, useState } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import { api, mensajeDe, type Publicacion, type Transaccion } from '../api'
import { useSesion } from '../sesion'
import { Cargando, claseBoton, claseTarjeta, detalleDe, Foto, Mensaje, precioTexto, useInstituciones } from '../ui'

export default function Detalle() {
  const { id } = useParams()
  const { usuario } = useSesion()
  const instituciones = useInstituciones()
  const navegar = useNavigate()
  const ubicacion = useLocation()
  const [pub, setPub] = useState<Publicacion | null>(null)
  const [error, setError] = useState('')
  const [enviando, setEnviando] = useState(false)

  useEffect(() => {
    api<Publicacion>(`/api/publicaciones/${id}`).then(setPub).catch((e) => setError(mensajeDe(e)))
  }, [id])

  if (error && !pub) return <Mensaje>{error}</Mensaje>
  if (!pub) return <Cargando />

  async function reservar() {
    if (!usuario) {
      navegar('/ingresar', { state: { desde: ubicacion.pathname, motivo: 'Para reservar un artículo necesitás una cuenta.' } })
      return
    }
    setEnviando(true)
    setError('')
    try {
      const t = await api<Transaccion>('/api/transacciones/', 'POST', { publicacion_id: pub!.id })
      navegar(`/transacciones/${t.id}`)
    } catch (e) {
      setError(mensajeDe(e))
      setEnviando(false)
    }
  }

  const esMia = usuario?.id === pub.vendedor_id

  return (
    <div className="mx-auto flex w-full max-w-xl flex-col gap-3.5">
      <div className="flex snap-x gap-2 overflow-x-auto">
        {(pub.imagenes_urls.length ? pub.imagenes_urls : [null]).map((url, i) => (
          <Foto key={url ?? i} url={url} indice={i} alt={`Foto ${i + 1} de ${pub.titulo}`} className="h-72 w-full shrink-0 snap-center rounded-[20px]" />
        ))}
      </div>
      <section className={`${claseTarjeta} flex flex-col gap-2 p-4`}>
        <h1 className="font-mano text-[40px] leading-[1.05]">{pub.titulo}</h1>
        <div className="text-[13px] text-suave">{detalleDe(pub, instituciones)}</div>
        <div className="font-mano text-[34px] leading-none">{precioTexto(pub.tipo, pub.precio)}</div>
        {pub.descripcion && <p className="leading-relaxed whitespace-pre-line">{pub.descripcion}</p>}
      </section>
      <Mensaje>{error}</Mensaje>
      {pub.estado !== 'disponible'
        ? <Mensaje tipo="info">Este artículo ya no está disponible.</Mensaje>
        : esMia
          ? <Mensaje tipo="info">Esta publicación es tuya.</Mensaje>
          : <button type="button" className={claseBoton} disabled={enviando} onClick={reservar}>{pub.tipo === 'venta' ? 'Reservar' : 'Pedir esta donación'}</button>}
      {pub.tipo === 'venta' && pub.estado === 'disponible' && !esMia && (
        <p className="text-center text-sm text-suave italic">Tu plata queda retenida hasta que recibís el artículo.</p>
      )}
    </div>
  )
}
