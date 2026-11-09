import { useCallback, useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, mensajeDe, type Publicacion } from '../api'
import { useSesion } from '../sesion'
import { guardarUbicacion, leerUbicacion, nombreUbicacion, SelectorUbicacion } from '../ubicacion'
import { Cargando, claseCampo, claseEtiqueta, claseSecundario, claseTarjeta, detalleDe, Foto, Icono, Mensaje, Panel, precioTexto, Titulo, useInstituciones } from '../ui'

const POR_PAGINA = 20
export const CATEGORIAS = [['indumentaria', 'Indumentaria'], ['utiles', 'Útiles'], ['libros', 'Libros'], ['instrumentos', 'Instrumentos'], ['deportes', 'Deportes']]
export const TALLES = ['4', '6', '8', '10', '12', '14', '16', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'Unico']

export default function Catalogo() {
  const { usuario, salir } = useSesion()
  const instituciones = useInstituciones()
  const [ubicacion, setUbicacion] = useState(leerUbicacion)
  const [filtros, setFiltros] = useState({ tipo: '', categoria: '', talle: '' })
  const [panel, setPanel] = useState<'ubicacion' | 'filtros' | null>(null)
  const [items, setItems] = useState<Publicacion[]>([])
  const [hayMas, setHayMas] = useState(true)
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState('')
  // Descarta las respuestas de un pedido viejo cuando cambian los filtros mientras carga
  const pedido = useRef(0)

  const parametros = new URLSearchParams(
    Object.entries({ ...ubicacion, ...filtros }).filter(([, v]) => v),
  ).toString()

  const cargar = useCallback(async (offset: number) => {
    const numero = ++pedido.current
    setCargando(true)
    setError('')
    try {
      const pagina = await api<Publicacion[]>(`/api/publicaciones/?limit=${POR_PAGINA}&offset=${offset}&${parametros}`)
      if (numero !== pedido.current) return
      setItems((anteriores) => (offset === 0 ? pagina : [...anteriores, ...pagina]))
      setHayMas(pagina.length === POR_PAGINA)
    } catch (e) {
      if (numero === pedido.current) {
        setError(mensajeDe(e))
        setHayMas(false)
      }
    } finally {
      if (numero === pedido.current) setCargando(false)
    }
  }, [parametros])

  useEffect(() => {
    cargar(0)
  }, [cargar])

  // Scroll infinito: al asomarse el final de la lista se pide el bloque siguiente
  const final = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!final.current || !hayMas || cargando) return
    const observador = new IntersectionObserver(([entrada]) => {
      if (entrada.isIntersecting) cargar(items.length)
    }, { rootMargin: '300px' })
    observador.observe(final.current)
    return () => observador.disconnect()
  }, [cargar, hayMas, cargando, items.length])

  function cambiarUbicacion(nueva: typeof ubicacion) {
    setUbicacion(nueva)
    guardarUbicacion(nueva)
  }

  const cambiarFiltro = (campo: keyof typeof filtros) => (e: React.ChangeEvent<HTMLSelectElement>) =>
    setFiltros({ ...filtros, [campo]: e.target.value })

  const cantidadFiltros = Object.values(filtros).filter(Boolean).length

  const camposUbicacion = <SelectorUbicacion instituciones={instituciones} valor={ubicacion} cambiar={cambiarUbicacion} />
  const camposFiltros = (
    <>
      <label className={claseEtiqueta}>
        Tipo
        <select className={claseCampo} value={filtros.tipo} onChange={cambiarFiltro('tipo')}>
          <option value="">Ventas y donaciones</option>
          <option value="venta">Ventas</option>
          <option value="donacion">Donaciones</option>
        </select>
      </label>
      <label className={claseEtiqueta}>
        Categoría
        <select className={claseCampo} value={filtros.categoria} onChange={cambiarFiltro('categoria')}>
          <option value="">Todas</option>
          {CATEGORIAS.map(([v, nombre]) => <option key={v} value={v}>{nombre}</option>)}
        </select>
      </label>
      <label className={claseEtiqueta}>
        Talle
        <select className={claseCampo} value={filtros.talle} onChange={cambiarFiltro('talle')}>
          <option value="">Todos</option>
          {TALLES.map((t) => <option key={t} value={t}>{t === 'Unico' ? 'Único' : t}</option>)}
        </select>
      </label>
    </>
  )

  return (
    <>
      <div className="flex items-center justify-between">
        <Titulo>Catálogo</Titulo>
        {usuario
          ? <button type="button" className={`${claseSecundario} md:hidden`} onClick={salir}>Salir</button>
          : <Link to="/ingresar" className="flex min-h-11 items-center rounded-full bg-naranja px-4.5 font-bold md:hidden">Ingresar</Link>}
      </div>

      <div className="flex items-center gap-2 lg:hidden">
        <button type="button" className={`${claseSecundario} min-w-0 text-sm font-semibold`} onClick={() => setPanel('ubicacion')}>
          <span className="text-naranja"><Icono tamano={18} d="M12 21s7-6.2 7-11.5A7 7 0 0 0 5 9.5C5 14.8 12 21 12 21zM12 12a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z" /></span>
          <span className="truncate">{nombreUbicacion(ubicacion, instituciones)}</span>
        </button>
        <button type="button" className={`${claseSecundario} text-sm font-semibold`} onClick={() => setPanel('filtros')} aria-label={`Personalizar filtros${cantidadFiltros ? `, ${cantidadFiltros} activos` : ''}`}>
          <Icono tamano={20}><path d="M4 7h10M18 7h2M4 17h2M10 17h10" /><circle cx="16" cy="7" r="2" /><circle cx="8" cy="17" r="2" /></Icono>
          {cantidadFiltros > 0 && <span>{cantidadFiltros}</span>}
        </button>
      </div>

      <Mensaje>{error}</Mensaje>

      <div className="lg:grid lg:grid-cols-[280px_minmax(0,1fr)] lg:items-start lg:gap-8">
        <aside aria-label="Filtros" className={`${claseTarjeta} sticky top-24 hidden max-h-[calc(100dvh-7rem)] flex-col gap-3 overflow-y-auto p-5 lg:flex`}>
          <h2 className="font-mano text-[28px] leading-[1.1]">¿Dónde buscás?</h2>
          {camposUbicacion}
          <h2 className="mt-2 font-mano text-[28px] leading-[1.1]">Personalizar</h2>
          {camposFiltros}
        </aside>

        <div className="flex flex-col gap-3.5">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:gap-5 xl:grid-cols-4">
            {items.map((p, i) => (
              <Link key={p.id} to={`/publicaciones/${p.id}`} className={`${claseTarjeta} relative flex flex-col overflow-hidden transition hover:-translate-y-0.5 hover:shadow-lg`}>
                <Foto url={p.imagenes_urls[0]} indice={i} alt="" className="h-28 w-full sm:h-36 lg:h-48" />
                <div className="flex flex-col gap-0.5 p-2.5 lg:p-3.5">
                  <div className="text-sm font-semibold lg:text-[15px]">{p.titulo}</div>
                  <div className="text-xs text-suave lg:text-[13px]">{detalleDe(p, instituciones)}</div>
                </div>
                <div className={`absolute top-2 right-2 rotate-3 rounded-xl px-2.5 font-mano text-[22px] leading-tight ${p.tipo === 'donacion' ? 'bg-menta' : 'bg-amarillo'}`}>
                  {precioTexto(p.tipo, p.precio)}
                </div>
              </Link>
            ))}
          </div>

          {cargando && <Cargando />}
          {!cargando && !error && items.length === 0 && (
            <p className="py-8 text-center text-suave">No hay artículos con esos filtros. Probá ampliar la búsqueda.</p>
          )}
          <div ref={final} />
        </div>
      </div>

      <Panel abierto={panel === 'ubicacion'} cerrar={() => setPanel(null)} titulo="¿Dónde buscás?">
        {camposUbicacion}
      </Panel>

      <Panel abierto={panel === 'filtros'} cerrar={() => setPanel(null)} titulo="Personalizar">
        {camposFiltros}
      </Panel>
    </>
  )
}
