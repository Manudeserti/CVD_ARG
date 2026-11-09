import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { guardarUbicacion, SelectorUbicacion, SIN_UBICACION } from '../ubicacion'
import { claseBoton, Logo, useInstituciones } from '../ui'

const CLAVE = 'cvd_vio_bienvenida'

export const yaVioBienvenida = () => localStorage.getItem(CLAVE) === 'si'
const marcarVista = () => localStorage.setItem(CLAVE, 'si')

const PASOS = [
  ['Elegí', 'Buscá por colegio, ciudad o talle el uniforme o útil que necesitás.'],
  ['Pagá seguro', 'Tu plata queda retenida hasta que tengas el artículo.'],
  ['Encontrate', 'Al recibirlo, el vendedor escanea tu código y listo. Las donaciones no se pagan.'],
]

/** En PC van dentro del cartel azul, para que la otra mitad quede solo con los desplegables. */
function Pasos({ className, claseTexto }: { className: string; claseTexto: string }) {
  return (
    <ol className={className}>
      {PASOS.map(([titulo, texto], i) => (
        <li key={titulo} className="flex items-start gap-3">
          <span className={`flex size-9 shrink-0 items-center justify-center rounded-full font-bold text-tinta ${['bg-cielo', 'bg-amarillo', 'bg-menta'][i]}`}>{i + 1}</span>
          <div>
            <div className="font-mano text-[26px] leading-[1.1]">{titulo}</div>
            <p className={`text-sm ${claseTexto}`}>{texto}</p>
          </div>
        </li>
      ))}
    </ol>
  )
}

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
    <div className="flex min-h-dvh flex-col lg:grid lg:grid-cols-2">
      <header className="flex flex-col gap-2.5 rounded-b-[36px] bg-tinta px-5 pt-5 pb-6 text-white md:px-10 md:py-10 lg:justify-center lg:gap-6 lg:rounded-none lg:px-16 xl:px-24">
        <Logo className="h-11 w-fit lg:h-16" />
        <h1 className="font-mano text-[62px] leading-[0.98] md:text-[88px] lg:text-[112px] xl:text-[136px]">
          <span className="block text-naranja">Comprá.</span>
          <span className="block text-amarillo">Vendé.</span>
          <span className="block text-menta">Doná.</span>
        </h1>
        <p className="text-sm text-[#c9d2e0] italic md:text-base lg:text-lg">Lo que a tu hijo ya no le queda, a otro le queda justo.</p>
        <Pasos className="mt-4 hidden flex-col gap-4 lg:flex" claseTexto="text-[#c9d2e0]" />
      </header>

      <main className="mx-auto flex w-full max-w-md flex-col gap-5 px-4 pt-5 pb-6 md:max-w-2xl md:gap-8 md:px-6 md:pt-10 lg:max-w-lg lg:justify-center lg:py-12">
        <Pasos className="flex flex-col gap-2.5 md:grid md:grid-cols-3 md:gap-5 lg:hidden" claseTexto="text-suave" />

        <section className="flex flex-col gap-3 lg:gap-4">
          <h2 className="resaltado self-start px-2 font-mano text-[32px] leading-[1.1] lg:text-[48px]">¿Dónde buscás?</h2>
          <div className="grid gap-3 md:grid-cols-3 lg:grid-cols-1 lg:gap-4">
            <SelectorUbicacion instituciones={instituciones} valor={ubicacion} cambiar={setUbicacion} />
          </div>
        </section>

        <div className="flex flex-col items-center gap-1">
          <button type="button" className={claseBoton} onClick={verArticulos}>Ver artículos</button>
          <Link to="/ingresar" onClick={marcarVista} className="flex min-h-11 items-center text-sm underline">Ya tengo cuenta</Link>
        </div>
      </main>
    </div>
  )
}
