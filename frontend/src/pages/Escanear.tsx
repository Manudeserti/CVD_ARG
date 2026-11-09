import { Scanner } from '@yudiel/react-qr-scanner'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api, mensajeDe } from '../api'
import { claseBoton, Icono, Mensaje, Titulo } from '../ui'

const ES_TOKEN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

export default function Escanear() {
  const navegar = useNavigate()
  const [procesando, setProcesando] = useState(false)
  const [listo, setListo] = useState(false)
  const [error, setError] = useState('')

  async function leer(valor: string) {
    if (procesando) return
    if (!ES_TOKEN.test(valor)) {
      setError('Ese código no es de una entrega de CVD.')
      return
    }
    setProcesando(true)
    setError('')
    try {
      await api('/api/transacciones/liberar', 'POST', { qr_token: valor })
      setListo(true)
    } catch (e) {
      setError(mensajeDe(e))
    } finally {
      setProcesando(false)
    }
  }

  return (
    <main className="mx-auto flex max-w-md flex-col gap-5 px-4 pt-3.5 pb-6">
      <div className="flex items-center gap-2">
        <button type="button" aria-label="Volver" onClick={() => navegar(-1)} className="flex size-11 shrink-0 items-center justify-center rounded-full border border-linea bg-white">
          <Icono tamano={22} d="M15 6l-6 6 6 6" />
        </button>
        <Titulo>Confirmar entrega</Titulo>
      </div>

      {listo ? (
        <>
          <Mensaje tipo="info">¡Entrega confirmada! La operación quedó cerrada.</Mensaje>
          <Link to="/transacciones" className={claseBoton}>Ver mis operaciones</Link>
        </>
      ) : (
        <>
          <p className="text-center text-[17px] leading-snug font-semibold">Apuntá la cámara al código del comprador</p>
          <div className="mx-auto aspect-square w-full max-w-80 overflow-hidden rounded-[28px] bg-tinta">
            <Scanner
              onScan={(codigos) => codigos[0] && leer(codigos[0].rawValue)}
              onError={() => setError('No pudimos usar la cámara. Revisá que el navegador tenga permiso.')}
              constraints={{ facingMode: 'environment' }}
              formats={['qr_code']}
              paused={procesando}
              sound={false}
            />
          </div>
          <Mensaje>{error}</Mensaje>
          <p className="mx-auto max-w-80 text-center text-sm text-suave italic">Escaneá solo después de entregar el artículo. Con el escaneo se libera el pago y la operación queda cerrada.</p>
        </>
      )}
    </main>
  )
}
