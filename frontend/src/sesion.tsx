import { createContext, useContext, useState, type ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { api, guardarSesion, leerSesion, type Sesion, type Usuario } from './api'

interface ContextoSesion {
  usuario: Usuario | null
  ingresar: (email: string, password: string) => Promise<void>
  salir: () => void
}

const Contexto = createContext<ContextoSesion | null>(null)

export function ProveedorSesion({ children }: { children: ReactNode }) {
  const [sesion, setSesion] = useState<Sesion | null>(leerSesion)

  async function ingresar(email: string, password: string) {
    const r = await api<{ access_token: string; usuario: Usuario }>('/api/usuarios/login', 'POST', { email, password })
    const nueva = { token: r.access_token, usuario: r.usuario }
    guardarSesion(nueva)
    setSesion(nueva)
  }

  function salir() {
    guardarSesion(null)
    setSesion(null)
  }

  return <Contexto.Provider value={{ usuario: sesion?.usuario ?? null, ingresar, salir }}>{children}</Contexto.Provider>
}

export function useSesion() {
  const contexto = useContext(Contexto)
  if (!contexto) throw new Error('useSesion necesita ProveedorSesion')
  return contexto
}

/** Pide ingresar solo cuando hace falta, y al terminar vuelve a esta misma pantalla. */
export function Privada({ children, motivo, soloAdmin }: { children: ReactNode; motivo: string; soloAdmin?: boolean }) {
  const { usuario } = useSesion()
  const ubicacion = useLocation()
  if (!usuario) return <Navigate to="/ingresar" replace state={{ desde: ubicacion.pathname, motivo }} />
  if (soloAdmin && usuario.rol !== 'admin') return <Navigate to="/" replace />
  return children
}
