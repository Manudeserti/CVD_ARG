import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { guardarUbicacion, SelectorUbicacion, SIN_UBICACION } from '../ubicacion'
import { claseBoton, useInstituciones } from '../ui'

const CLAVE = 'cvd_vio_bienvenida'

export const yaVioBienvenida = () => localStorage.getItem(CLAVE) === 'si'
const marcarVista = () => localStorage.setItem(CLAVE, 'si')

const PASOS = [
  ['Elegí', 'Buscá por colegio, ciudad o talle el uniforme o útil que necesitás.'],
  ['Pagá seguro', 'Tu plata queda retenida hasta que tengas el artículo.'],
  ['Encontrate', 'Al recibirlo, el vendedor escanea tu código y listo. Las donaciones no se pagan.'],
]

export default function Bienvenida() {
  const instituciones = useInstituciones()
  const [ubicacion, setUbicacion] = useState(SIN_UBICACION)
  const navegar = useNavigate()

  function verArticulos() {
    marcarVista()
    guardarUbicacion(ubicacion)
    navegar('/', { replace: true })
  }

  return (
    <div className="mx-auto flex min-h-dvh max-w-md flex-col">
      <header className="flex flex-col gap-2.5 rounded-b-[36px] bg-tinta px-5 pt-5 pb-6 text-white">
        <div className="text-xl font-bold tracking-wider text-naranja">CVD</div>
        <h1 className="font-mano text-[62px] leading-[0.98]">
          <span className="block text-naranja">Comprá.</span>
          <span className="block text-amarillo">Vendé.</span>
          <span className="block text-menta">Doná.</span>
        </h1>
        <p className="text-sm text-[#c9d2e0] italic">Lo que a tu hijo ya no le queda, a otro le queda justo.</p>
      </header>

      <main className="flex flex-col gap-5 px-4 pt-5 pb-6">
        <ol className="flex flex-col gap-2.5">
          {PASOS.map(([titulo, texto], i) => (
            <li key={titulo} className="flex items-start gap-3">
              <span className={`flex size-9 shrink-0 items-center justify-center rounded-full font-bold ${['bg-cielo', 'bg-amarillo', 'bg-menta'][i]}`}>{i + 1}</span>
              <div>
                <div className="font-mano text-[26px] leading-[1.1]">{titulo}</div>
                <p className="text-sm text-suave">{texto}</p>
              </div>
            </li>
          ))}
        </ol>

        <section className="flex flex-col gap-3">
          <h2 className="resaltado self-start px-2 font-mano text-[32px] leading-[1.1]">¿Dónde buscás?</h2>
          <SelectorUbicacion instituciones={instituciones} valor={ubicacion} cambiar={setUbicacion} />
        </section>

        <div className="flex flex-col items-center gap-1">
          <button type="button" className={claseBoton} onClick={verArticulos}>Ver artículos</button>
          <Link to="/ingresar" onClick={marcarVista} className="flex min-h-11 items-center text-sm underline">Ya tengo cuenta</Link>
        </div>
      </main>
    </div>
  )
}
