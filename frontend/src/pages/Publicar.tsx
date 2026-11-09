import { useState, type ChangeEvent, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, mensajeDe, type Tipo } from '../api'
import { subirFoto } from '../fotos'
import { SelectorColegio, SIN_LUGAR, type Lugar } from '../ubicacion'
import { claseBoton, claseCampo, claseEtiqueta, Icono, Mensaje, Titulo, useInstituciones } from '../ui'
import { CATEGORIAS, TALLES } from './Catalogo'

const MAX_FOTOS = 5

export default function Publicar() {
  const instituciones = useInstituciones()
  const navegar = useNavigate()
  const [fotos, setFotos] = useState<string[]>([])
  const [subiendo, setSubiendo] = useState(false)
  const [datos, setDatos] = useState({ titulo: '', descripcion: '', categoria: 'indumentaria', talle: '', precio: '' })
  const [tipo, setTipo] = useState<Tipo>('venta')
  const [lugar, setLugar] = useState(SIN_LUGAR)
  const [colegio, setColegio] = useState<number | null>(null)
  const [pidiendoAlta, setPidiendoAlta] = useState(false)
  const [nombreNuevo, setNombreNuevo] = useState('')
  const [error, setError] = useState('')
  const [enviando, setEnviando] = useState(false)

  const campo = (nombre: keyof typeof datos) => ({
    value: datos[nombre],
    onChange: (e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => setDatos({ ...datos, [nombre]: e.target.value }),
  })

  async function agregarFotos(e: ChangeEvent<HTMLInputElement>) {
    const elegidas = [...(e.target.files ?? [])].slice(0, MAX_FOTOS - fotos.length)
    e.target.value = ''
    setSubiendo(true)
    setError('')
    try {
      for (const archivo of elegidas) {
        const url = await subirFoto(archivo)
        setFotos((actuales) => [...actuales, url])
      }
    } catch (err) {
      setError(mensajeDe(err))
    } finally {
      setSubiendo(false)
    }
  }

  function cambiarLugar(valor: Lugar) {
    setLugar(valor)
    setColegio(null)
  }

  async function enviar(e: FormEvent) {
    e.preventDefault()
    if (!pidiendoAlta && colegio === null) {
      setError('Elegí el colegio o pedí que lo demos de alta.')
      return
    }
    setEnviando(true)
    setError('')
    try {
      await api('/api/publicaciones/', 'POST', {
        titulo: datos.titulo,
        descripcion: datos.descripcion || null,
        categoria: datos.categoria,
        talle: datos.categoria === 'indumentaria' && datos.talle ? datos.talle : null,
        tipo,
        precio: tipo === 'venta' ? datos.precio : 0,
        imagenes_urls: fotos,
        institucion_id: pidiendoAlta ? null : colegio,
        colegio_nuevo: pidiendoAlta ? { nombre: nombreNuevo, ciudad: lugar.ciudad.trim(), provincia: lugar.provincia } : null,
      })
      navegar('/mis-publicaciones')
    } catch (err) {
      setError(mensajeDe(err))
      setEnviando(false)
    }
  }

  const opcionTipo = (valor: Tipo, texto: string) => (
    <button type="button" aria-pressed={tipo === valor} onClick={() => setTipo(valor)} className={`h-11 rounded-full font-medium ${tipo === valor ? 'bg-tinta font-semibold text-white' : ''}`}>{texto}</button>
  )

  return (
    <form onSubmit={enviar} className="mx-auto grid w-full max-w-xl items-start gap-3 lg:max-w-5xl lg:grid-cols-2 lg:gap-x-10">
      <div className="lg:col-span-2"><Titulo>Publicar</Titulo></div>

      <div className="flex flex-col gap-3">
      <div className="flex flex-col gap-1.5">
        <div className="text-[13px] font-medium">Fotos (hasta {MAX_FOTOS})</div>
        <div className="flex flex-wrap gap-2">
          {fotos.map((url) => (
            <div key={url} className="relative size-21">
              <img src={url} alt="Foto del artículo" className="size-full rounded-2xl object-cover" />
              <button type="button" aria-label="Quitar foto" onClick={() => setFotos(fotos.filter((f) => f !== url))} className="absolute -top-1 -right-1 flex size-7 items-center justify-center rounded-full bg-tinta text-white">
                <Icono tamano={14} d="M6 6l12 12M18 6L6 18" />
              </button>
            </div>
          ))}
          {fotos.length < MAX_FOTOS && (
            <label className="flex size-21 cursor-pointer items-center justify-center rounded-2xl border border-dashed border-tinta bg-white focus-within:outline-2">
              <span className="sr-only">Agregar fotos</span>
              {subiendo ? <span className="text-xs">Subiendo…</span> : <Icono tamano={26} d="M12 5v14M5 12h14" />}
              <input type="file" accept="image/*" multiple className="sr-only" disabled={subiendo} onChange={agregarFotos} />
            </label>
          )}
        </div>
      </div>

      <label className={claseEtiqueta}>Título<input className={claseCampo} required minLength={3} maxLength={100} {...campo('titulo')} /></label>

      <div className="flex flex-col gap-1">
        <div className="text-[13px] font-medium">Tipo de publicación</div>
        <div className="grid grid-cols-2 gap-1 rounded-3xl border border-linea bg-white p-1">
          {opcionTipo('venta', 'Venta')}
          {opcionTipo('donacion', 'Donación')}
        </div>
      </div>

      {tipo === 'venta' && (
        <label className={claseEtiqueta}>
          Precio
          <input className={claseCampo} type="number" inputMode="decimal" min="1" step="0.01" required {...campo('precio')} />
          <span className="font-normal text-suave">La plataforma cobra una comisión del 5 %.</span>
        </label>
      )}

      <div className="grid grid-cols-2 gap-2.5">
        <label className={claseEtiqueta}>
          Categoría
          <select className={claseCampo} {...campo('categoria')}>{CATEGORIAS.map(([v, nombre]) => <option key={v} value={v}>{nombre}</option>)}</select>
        </label>
        {datos.categoria === 'indumentaria' && (
          <label className={claseEtiqueta}>
            Talle
            <select className={claseCampo} {...campo('talle')}>
              <option value="">Sin indicar</option>
              {TALLES.map((t) => <option key={t} value={t}>{t === 'Unico' ? 'Único' : t}</option>)}
            </select>
          </label>
        )}
      </div>

      <label className={claseEtiqueta}>Descripción<textarea rows={2} maxLength={2000} className="rounded-2xl border border-linea bg-white px-3.5 py-3 text-[15px] lg:min-h-28" {...campo('descripcion')} /></label>
      </div>

      <div className="flex flex-col gap-3">
      <SelectorColegio instituciones={instituciones} lugar={lugar} setLugar={cambiarLugar} colegio={pidiendoAlta ? null : colegio} setColegio={(id) => { setColegio(id); setPidiendoAlta(false) }} />

      {pidiendoAlta ? (
        <section className="flex flex-col gap-3 rounded-2xl border border-linea bg-white p-3.5">
          <label className={claseEtiqueta}>Nombre del colegio<input className={claseCampo} required minLength={3} maxLength={150} value={nombreNuevo} onChange={(e) => setNombreNuevo(e.target.value)} /></label>
          <p className="text-sm text-suave">Tu publicación queda pendiente y se publica cuando demos de alta el colegio. Estará mañana.</p>
          <button type="button" className="min-h-11 text-sm underline" onClick={() => setPidiendoAlta(false)}>Mejor elijo uno de la lista</button>
        </section>
      ) : (
        <button type="button" className="flex min-h-11 items-center text-left text-sm" onClick={() => { setPidiendoAlta(true); setColegio(null) }}>
          <span>¿No está tu colegio? <strong>Dalo de alta.</strong> Estará mañana.</span>
        </button>
      )}

      <Mensaje>{error}</Mensaje>
      <button className={claseBoton} disabled={enviando || subiendo}>{pidiendoAlta ? 'Publicar y pedir el alta' : 'Publicar'}</button>
      </div>
    </form>
  )
}
