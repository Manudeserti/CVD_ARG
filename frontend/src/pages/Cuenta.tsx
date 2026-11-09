import { useState, type FormEvent, type ReactNode } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { api, mensajeDe } from '../api'
import { useSesion } from '../sesion'
import { claseBoton, claseCampo, claseEtiqueta, Mensaje, Titulo } from '../ui'

type Vuelta = { desde?: string; motivo?: string } | null

function Marco({ titulo, motivo, children }: { titulo: string; motivo?: string; children: ReactNode }) {
  return (
    <main className="mx-auto flex max-w-md flex-col gap-3.5 px-4 pt-6 pb-8 md:mt-14 md:rounded-3xl md:border md:border-linea md:bg-white md:p-8 md:shadow-[0_2px_8px_rgba(23,35,59,0.06)]">
      <Link to="/" className="text-xl font-bold tracking-wider text-naranja">CVD</Link>
      <Titulo>{titulo}</Titulo>
      {motivo && <Mensaje tipo="info">{motivo}</Mensaje>}
      {children}
    </main>
  )
}

export function Ingresar() {
  const { ingresar } = useSesion()
  const navegar = useNavigate()
  const vuelta = useLocation().state as Vuelta
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [enviando, setEnviando] = useState(false)

  async function enviar(e: FormEvent) {
    e.preventDefault()
    setEnviando(true)
    setError('')
    try {
      await ingresar(email, password)
      navegar(vuelta?.desde ?? '/', { replace: true })
    } catch (err) {
      setError(mensajeDe(err))
      setEnviando(false)
    }
  }

  return (
    <Marco titulo="Ingresar" motivo={vuelta?.motivo}>
      <form onSubmit={enviar} className="flex flex-col gap-3">
        <label className={claseEtiqueta}>Correo<input className={claseCampo} type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} /></label>
        <label className={claseEtiqueta}>Contraseña<input className={claseCampo} type="password" autoComplete="current-password" required value={password} onChange={(e) => setPassword(e.target.value)} /></label>
        <Mensaje>{error}</Mensaje>
        <button className={claseBoton} disabled={enviando}>Ingresar</button>
      </form>
      <p className="text-center text-sm">¿No tenés cuenta? <Link to="/registro" state={vuelta} className="font-semibold underline">Registrate</Link></p>
    </Marco>
  )
}

export function Registro() {
  const { ingresar } = useSesion()
  const navegar = useNavigate()
  const vuelta = useLocation().state as Vuelta
  const [datos, setDatos] = useState({ nombre: '', apellido: '', email: '', telefono: '', password: '' })
  const [error, setError] = useState('')
  const [enviando, setEnviando] = useState(false)

  const campo = (nombre: keyof typeof datos) => ({
    value: datos[nombre],
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => setDatos({ ...datos, [nombre]: e.target.value }),
    className: claseCampo,
  })

  async function enviar(e: FormEvent) {
    e.preventDefault()
    setEnviando(true)
    setError('')
    try {
      await api('/api/usuarios/', 'POST', { ...datos, telefono: datos.telefono || null })
      await ingresar(datos.email, datos.password)
      navegar(vuelta?.desde ?? '/', { replace: true })
    } catch (err) {
      setError(mensajeDe(err))
      setEnviando(false)
    }
  }

  return (
    <Marco titulo="Crear cuenta" motivo={vuelta?.motivo}>
      <form onSubmit={enviar} className="flex flex-col gap-3">
        <div className="grid grid-cols-2 gap-2.5">
          <label className={claseEtiqueta}>Nombre<input {...campo('nombre')} autoComplete="given-name" required minLength={2} /></label>
          <label className={claseEtiqueta}>Apellido<input {...campo('apellido')} autoComplete="family-name" required minLength={2} /></label>
        </div>
        <label className={claseEtiqueta}>Correo<input {...campo('email')} type="email" autoComplete="email" required /></label>
        <label className={claseEtiqueta}>Teléfono (opcional)<input {...campo('telefono')} type="tel" autoComplete="tel" maxLength={20} /></label>
        <label className={claseEtiqueta}>Contraseña (8 caracteres o más)<input {...campo('password')} type="password" autoComplete="new-password" required minLength={8} /></label>
        <Mensaje>{error}</Mensaje>
        <button className={claseBoton} disabled={enviando}>Crear cuenta</button>
      </form>
      <p className="text-center text-sm">¿Ya tenés cuenta? <Link to="/ingresar" state={vuelta} className="font-semibold underline">Ingresá</Link></p>
    </Marco>
  )
}
