import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, mensajeDe, type EstadoPago, type Transaccion } from '../api'
import { useSesion } from '../sesion'
import { Cargando, Mensaje, precioTexto, TarjetaArticulo, Titulo } from '../ui'

export const ESTADOS_PAGO: Record<EstadoPago, string> = {
  pendiente: 'Reservado',
  retenido: 'Pago retenido',
  liberado: 'Entregado',
  cancelado: 'Cancelado',
  reembolsado: 'Devuelto',
}

export default function Transacciones() {
  const { usuario } = useSesion()
  const [items, setItems] = useState<Transaccion[] | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api<Transaccion[]>('/api/transacciones/mis-transacciones').then(setItems).catch((e) => setError(mensajeDe(e)))
  }, [])

  return (
    <>
      <Titulo>Operaciones</Titulo>
      <Mensaje>{error}</Mensaje>
      {items === null && !error && <Cargando />}
      {items?.length === 0 && <p className="py-8 text-center text-suave">Todavía no tenés operaciones.</p>}
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {items?.map((t, i) => (
          <Link key={t.id} to={`/transacciones/${t.id}`}>
            <TarjetaArticulo
              titulo={t.titulo ?? 'Artículo'}
              detalle={`${t.comprador_id === usuario?.id ? 'Comprás' : 'Vendés'} · ${ESTADOS_PAGO[t.estado_pago]}`}
              precio={precioTexto(t.tipo, t.monto)}
              foto={t.imagen}
              indice={i}
            />
          </Link>
        ))}
      </div>
    </>
  )
}
