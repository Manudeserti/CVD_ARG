import { QRCodeSVG } from 'qrcode.react'
import { useCallback, useEffect, useState } from 'react'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import { api, mensajeDe, type Contacto, type Transaccion as Operacion } from '../api'
import { useSesion } from '../sesion'
import { Cargando, claseBoton, claseSecundario, claseTarjeta, Mensaje, precioTexto, TarjetaArticulo, Titulo } from '../ui'

const REINTENTOS_PAGO = 10
const ESPERA_PAGO_MS = 3000

function Pasos({ op }: { op: Operacion }) {
  const pasos = op.tipo === 'donacion' ? ['Reservado', 'Entregado'] : ['Reservado', 'Pagado', 'Entregado']
  const actual = op.estado_pago === 'liberado' ? pasos.length - 1 : op.estado_pago === 'retenido' ? 1 : 0
  return (
    <ol aria-label="Estado de la operación" className="grid gap-1.5" style={{ gridTemplateColumns: `repeat(${pasos.length}, minmax(0, 1fr))` }}>
      {pasos.map((paso, i) => (
        <li key={paso} aria-current={i === actual ? 'step' : undefined} className={`flex flex-col gap-1.5 text-[13px] ${i === actual ? 'font-bold' : i > actual ? 'text-suave' : ''}`}>
          <div className={`h-2 rounded ${i <= actual ? 'bg-naranja' : 'bg-linea'}`} />
          {paso}
        </li>
      ))}
    </ol>
  )
}

export default function Transaccion() {
  const { id } = useParams()
  const { usuario } = useSesion()
  const [volvioDePagar] = useSearchParams()
  const [op, setOp] = useState<Operacion | null>(null)
  const [contacto, setContacto] = useState<Contacto | null>(null)
  const [cargada, setCargada] = useState(false)
  const [error, setError] = useState('')
  const [enviando, setEnviando] = useState(false)

  const cargar = useCallback(async () => {
    const todas = await api<Operacion[]>('/api/transacciones/mis-transacciones')
    setOp(todas.find((t) => t.id === id) ?? null)
    setCargada(true)
  }, [id])

  useEffect(() => {
    cargar().catch((e) => {
      setError(mensajeDe(e))
      setCargada(true)
    })
  }, [cargar])

  const estado = op?.estado_pago
  const esComprador = op?.comprador_id === usuario?.id
  // Donación: el encuentro se habilita al reservar. Venta: recién con el pago retenido.
  const enEncuentro = op !== null && ((op.tipo === 'venta' && estado === 'retenido') || (op.tipo === 'donacion' && estado === 'pendiente'))
  const hayContacto = enEncuentro || estado === 'liberado'

  useEffect(() => {
    if (!hayContacto) return
    api<Contacto>(`/api/transacciones/${id}/contacto`).then(setContacto).catch(() => setContacto(null))
  }, [hayContacto, id])

  // El aviso de Mercado Pago puede llegar unos segundos después de que el comprador vuelve
  const pagoEnCamino = volvioDePagar.get('status') === 'approved' && estado === 'pendiente'
  useEffect(() => {
    if (!pagoEnCamino) return
    let intentos = 0
    const reloj = setInterval(() => {
      if (++intentos > REINTENTOS_PAGO) clearInterval(reloj)
      else cargar().catch(() => undefined)
    }, ESPERA_PAGO_MS)
    return () => clearInterval(reloj)
  }, [pagoEnCamino, cargar])

  if (!cargada) return <Cargando />
  if (!op) return <><Titulo>Operaciones</Titulo><Mensaje>{error || 'No encontramos esa operación.'}</Mensaje></>

  async function pagar() {
    setEnviando(true)
    setError('')
    try {
      const { url_pago } = await api<{ url_pago: string }>(`/api/transacciones/${id}/pago`, 'POST')
      window.location.href = url_pago
    } catch (e) {
      setError(mensajeDe(e))
      setEnviando(false)
    }
  }

  async function cancelar() {
    const hayPlata = estado === 'retenido'
    if (!window.confirm(hayPlata ? '¿Cancelar la operación? La plata vuelve al comprador.' : '¿Cancelar la operación?')) return
    setEnviando(true)
    setError('')
    try {
      await api(`/api/transacciones/${id}/cancelar`, 'POST')
      await cargar()
    } catch (e) {
      setError(mensajeDe(e))
    } finally {
      setEnviando(false)
    }
  }

  const contraparte = esComprador ? 'el vendedor' : 'el comprador'
  const seCerro = estado === 'cancelado' || estado === 'reembolsado'

  return (
    <div className="mx-auto flex w-full max-w-xl flex-col gap-3.5 md:max-w-2xl">
      <Titulo>Operaciones</Titulo>
      <TarjetaArticulo titulo={op.titulo ?? 'Artículo'} detalle={esComprador ? 'Estás comprando' : 'Estás vendiendo'} precio={precioTexto(op.tipo, op.monto)} foto={op.imagen} indice={0} />
      {!seCerro && <Pasos op={op} />}
      <Mensaje>{error}</Mensaje>

      {seCerro && <Mensaje tipo="info">{estado === 'reembolsado' ? 'La operación se canceló y la plata volvió al comprador.' : 'La operación se canceló.'}</Mensaje>}
      {estado === 'liberado' && <Mensaje tipo="info">¡Entrega confirmada! La operación quedó cerrada.</Mensaje>}
      {pagoEnCamino && <Mensaje tipo="info">Estamos confirmando tu pago, puede tardar unos segundos.</Mensaje>}

      {op.tipo === 'venta' && estado === 'pendiente' && !pagoEnCamino && (
        <section className={`${claseTarjeta} flex flex-col gap-2.5 p-4`}>
          <h2 className="font-mano text-[32px] leading-[1.1]">Falta el pago</h2>
          {esComprador ? (
            <>
              <p className="leading-normal">Tenés 24 horas para pagar. Si no, el artículo vuelve al catálogo.</p>
              <p className="text-sm text-suave italic">Tu plata queda retenida hasta que recibís el artículo y el vendedor escanea tu código.</p>
              <button type="button" className={claseBoton} disabled={enviando} onClick={pagar}>Pagar con Mercado Pago</button>
            </>
          ) : <p className="leading-normal">El comprador tiene 24 horas para pagar. Cuando lo haga te mostramos sus datos.</p>}
        </section>
      )}

      {enEncuentro && esComprador && op.qr_token && (
        <section className={`${claseTarjeta} flex flex-col items-center gap-3 p-4`}>
          <h2 className="font-mano text-[32px] leading-[1.1]">Tu código de entrega</h2>
          <QRCodeSVG value={op.qr_token} size={210} fgColor="#17233B" title="Código QR de entrega" />
          <p className="text-center text-sm text-suave italic">Mostráselo a quien te lo entrega solo cuando tengas el artículo en la mano. Al escanearlo ya no se puede cancelar.</p>
        </section>
      )}

      {enEncuentro && !esComprador && (
        <Link to="/escanear" className={claseBoton}>Escanear el código</Link>
      )}

      {contacto && (
        <section className={`${claseTarjeta} flex flex-col gap-0.5 p-4`}>
          <h2 className="mb-1 font-mano text-[28px] leading-[1.1]">Coordiná con {contraparte}</h2>
          <div className="font-semibold">{contacto.nombre} {contacto.apellido}</div>
          {contacto.telefono && <a className="flex min-h-11 items-center underline" href={`tel:${contacto.telefono}`}>{contacto.telefono}</a>}
          <a className="flex min-h-11 items-center underline" href={`mailto:${contacto.email}`}>{contacto.email}</a>
        </section>
      )}

      {(estado === 'pendiente' || estado === 'retenido') && !pagoEnCamino && (
        <button type="button" className={claseSecundario} disabled={enviando} onClick={cancelar}>
          {estado === 'retenido' ? 'Cancelar y devolver la plata' : 'Cancelar la reserva'}
        </button>
      )}
    </div>
  )
}
