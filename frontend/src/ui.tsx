import { useEffect, useRef, useState, type ReactNode } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { api, type Institucion, type Publicacion, type Tipo } from './api'
import { useSesion } from './sesion'

export const claseBoton = 'flex min-h-13 w-full items-center justify-center rounded-full bg-naranja px-5 font-bold text-tinta disabled:opacity-60'
export const claseSecundario = 'flex min-h-11 items-center justify-center gap-1.5 rounded-full border border-linea bg-white px-4 font-medium text-tinta disabled:opacity-60'
export const claseCampo = 'h-12 w-full rounded-2xl border border-linea bg-white px-3.5 text-[15px] text-tinta'
export const claseTarjeta = 'rounded-[20px] border border-linea bg-white shadow-[0_2px_8px_rgba(23,35,59,0.06)]'
export const claseEtiqueta = 'flex flex-col gap-1 text-[13px] font-medium'

export function Titulo({ children }: { children: ReactNode }) {
  return <h1 className="resaltado w-fit px-2 font-mano text-[42px] leading-[1.1] md:text-[52px]">{children}</h1>
}

export function Mensaje({ children, tipo = 'error' }: { children: ReactNode; tipo?: 'error' | 'info' }) {
  if (!children) return null
  return (
    <p role={tipo === 'error' ? 'alert' : 'status'} className={`rounded-2xl p-3 text-sm ${tipo === 'error' ? 'bg-rosa' : 'bg-menta'}`}>
      {children}
    </p>
  )
}

export function Cargando() {
  return <p role="status" className="py-8 text-center text-suave">Cargando…</p>
}

export function precioTexto(tipo: Tipo | null, monto: string) {
  if (tipo === 'donacion') return 'Se dona'
  return `$ ${Number(monto).toLocaleString('es-AR', { maximumFractionDigits: 2 })}`
}

const COLORES = ['bg-cielo', 'bg-amarillo', 'bg-rosa', 'bg-menta']

export function Foto({ url, indice = 0, alt, className }: { url?: string | null; indice?: number; alt: string; className: string }) {
  if (url) return <img src={url} alt={alt} loading="lazy" className={`object-cover ${className}`} />
  return <div className={`flex items-center justify-center text-[13px] ${COLORES[indice % COLORES.length]} ${className}`}>Sin foto</div>
}

export function TarjetaArticulo({ titulo, detalle, precio, foto, indice }: { titulo: string; detalle: string; precio: string; foto?: string | null; indice: number }) {
  return (
    <div className={`${claseTarjeta} flex items-center gap-3 p-2`}>
      <Foto url={foto} indice={indice} alt="" className="size-19 shrink-0 rounded-[14px]" />
      <div className="min-w-0">
        <div className="font-semibold">{titulo}</div>
        <div className="text-[13px] text-suave">{detalle}</div>
        <div className="font-mano text-[26px] leading-[1.1]">{precio}</div>
      </div>
    </div>
  )
}

/** Panel modal. <dialog> ya resuelve el foco, la tecla Esc y el fondo. */
export function Panel({ abierto, cerrar, titulo, children }: { abierto: boolean; cerrar: () => void; titulo: string; children: ReactNode }) {
  const ref = useRef<HTMLDialogElement>(null)
  useEffect(() => {
    if (abierto) ref.current?.showModal()
    else ref.current?.close()
  }, [abierto])
  return (
    <dialog ref={ref} onClose={cerrar} className="m-auto w-[min(92vw,420px)] rounded-3xl bg-papel p-5 text-tinta">
      <h2 className="mb-3 font-mano text-[32px] leading-[1.1]">{titulo}</h2>
      <div className="flex flex-col gap-3">
        {children}
        <button type="button" className={claseBoton} onClick={cerrar}>Listo</button>
      </div>
    </dialog>
  )
}

export function useInstituciones() {
  const [instituciones, setInstituciones] = useState<Institucion[]>([])
  useEffect(() => {
    api<Institucion[]>('/api/instituciones/').then(setInstituciones).catch(() => setInstituciones([]))
  }, [])
  return instituciones
}

export function detalleDe(p: Publicacion, instituciones: Institucion[]) {
  const colegio = instituciones.find((i) => i.id === p.institucion_id)?.nombre
  return [p.talle && `Talle ${p.talle === 'Unico' ? 'único' : p.talle}`, colegio].filter(Boolean).join(' · ') || p.categoria
}

const iconos = {
  catalogo: <><rect x="4" y="4" width="7" height="7" rx="2" /><rect x="13" y="4" width="7" height="7" rx="2" /><rect x="4" y="13" width="7" height="7" rx="2" /><rect x="13" y="13" width="7" height="7" rx="2" /></>,
  publicar: <><circle cx="12" cy="12" r="9" /><path d="M12 8v8M8 12h8" /></>,
  articulos: <><path d="M20.6 13.4l-7.2 7.2a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8z" /><circle cx="8" cy="8" r="1.5" /></>,
  operaciones: <path d="M7 4L3 8l4 4M3 8h14M17 20l4-4-4-4M21 16H7" />,
}

export function Icono({ d, children, tamano = 24 }: { d?: string; children?: ReactNode; tamano?: number }) {
  return (
    <svg width={tamano} height={tamano} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {d ? <path d={d} /> : children}
    </svg>
  )
}

const destinos = [
  { a: '/', nombre: 'Catálogo', icono: iconos.catalogo },
  { a: '/publicar', nombre: 'Publicar', icono: iconos.publicar },
  { a: '/mis-publicaciones', nombre: 'Mis artículos', icono: iconos.articulos },
  { a: '/transacciones', nombre: 'Operaciones', icono: iconos.operaciones },
]

export function MenuSuperior() {
  const { usuario, salir } = useSesion()
  return (
    <header className="sticky top-0 z-10 hidden bg-tinta text-white md:block">
      <div className="mx-auto flex h-16 max-w-7xl items-center gap-2 px-6 lg:px-10">
        <Link to="/" className="mr-6 text-xl font-bold tracking-wider text-naranja">CVD</Link>
        <nav aria-label="Principal" className="flex items-center gap-1">
          {destinos.map((d) => (
            <NavLink key={d.a} to={d.a} end={d.a === '/'} className={({ isActive }) => `flex h-10 items-center gap-2 rounded-full px-4 text-sm font-semibold ${isActive ? 'bg-naranja text-tinta' : 'hover:bg-white/10'}`}>
              <Icono tamano={18}>{d.icono}</Icono>
              {d.nombre}
            </NavLink>
          ))}
        </nav>
        <div className="ml-auto">
          {usuario
            ? <button type="button" className="flex h-10 items-center rounded-full px-4 text-sm font-semibold hover:bg-white/10" onClick={salir}>Salir</button>
            : <Link to="/ingresar" className="flex h-10 items-center rounded-full bg-naranja px-5 text-sm font-bold text-tinta">Ingresar</Link>}
        </div>
      </div>
    </header>
  )
}

export function MenuInferior() {
  return (
    <nav aria-label="Principal" className="fixed inset-x-3 bottom-3 z-10 mx-auto grid h-17 max-w-md grid-cols-4 items-center rounded-full bg-tinta px-2 md:hidden">
      {destinos.map((d) => (
        <NavLink key={d.a} to={d.a} end={d.a === '/'} aria-label={d.nombre} className={({ isActive }) => `flex size-13 items-center justify-center justify-self-center rounded-full ${isActive ? 'bg-naranja text-tinta' : 'text-white'}`}>
          <Icono>{d.icono}</Icono>
        </NavLink>
      ))}
    </nav>
  )
}
