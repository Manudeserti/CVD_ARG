const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const CLAVE_SESION = 'cvd_sesion'

export interface Usuario {
  id: string
  nombre: string
  apellido: string
  rol: 'usuario' | 'admin'
}
export interface Sesion {
  token: string
  usuario: Usuario
}
export interface Institucion {
  id: number
  nombre: string
  ciudad: string
  provincia: string
}
export type EstadoPublicacion = 'disponible' | 'reservado' | 'vendido' | 'baja' | 'pendiente_colegio' | 'borrador'
export type Tipo = 'venta' | 'donacion'
export interface Publicacion {
  id: string
  vendedor_id: string
  institucion_id: number | null
  titulo: string
  descripcion: string | null
  categoria: string
  talle: string | null
  tipo: Tipo
  precio: string
  estado: EstadoPublicacion
  imagenes_urls: string[]
  aviso?: string | null
}
export type EstadoPago = 'pendiente' | 'retenido' | 'liberado' | 'cancelado' | 'reembolsado'
export interface Transaccion {
  id: string
  publicacion_id: string
  comprador_id: string
  vendedor_id: string
  monto: string
  estado_pago: EstadoPago
  qr_token: string | null
  titulo: string | null
  tipo: Tipo | null
  imagen: string | null
}
export interface Contacto {
  nombre: string
  apellido: string
  email: string
  telefono: string | null
}
export interface Solicitud {
  id: string
  nombre: string
  ciudad: string
  provincia: string
  publicacion_id: string
  publicacion_titulo: string
}

export function leerSesion(): Sesion | null {
  const guardada = localStorage.getItem(CLAVE_SESION)
  return guardada ? (JSON.parse(guardada) as Sesion) : null
}

export function guardarSesion(sesion: Sesion | null) {
  if (sesion) localStorage.setItem(CLAVE_SESION, JSON.stringify(sesion))
  else localStorage.removeItem(CLAVE_SESION)
}

export class ErrorApi extends Error {}

/** Llama a la API con la sesión actual. Si el token venció, cierra la sesión y lleva a ingresar. */
export async function api<T>(ruta: string, metodo = 'GET', cuerpo?: unknown): Promise<T> {
  const sesion = leerSesion()
  let respuesta: Response
  try {
    respuesta = await fetch(`${API}${ruta}`, {
      method: metodo,
      headers: {
        ...(cuerpo === undefined ? {} : { 'Content-Type': 'application/json' }),
        ...(sesion ? { Authorization: `Bearer ${sesion.token}` } : {}),
      },
      body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo),
    })
  } catch {
    throw new ErrorApi('No pudimos conectarnos. Revisá tu internet y probá de nuevo.')
  }

  if (respuesta.status === 401 && sesion) {
    guardarSesion(null)
    window.location.assign('/ingresar')
  }
  if (!respuesta.ok) {
    const error = await respuesta.json().catch(() => null)
    // FastAPI devuelve una lista cuando falla la validación de los datos
    throw new ErrorApi(typeof error?.detail === 'string' ? error.detail : 'Revisá los datos e intentá de nuevo.')
  }
  return respuesta.json() as Promise<T>
}

export function mensajeDe(error: unknown): string {
  return error instanceof ErrorApi ? error.message : 'Algo salió mal. Probá de nuevo.'
}
