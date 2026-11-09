import { api, ErrorApi } from './api'

const LADO_MAXIMO = 1600

/** Achica la foto a JPEG: las de celular pueden superar los 5 MB que acepta el bucket. */
async function achicar(archivo: File): Promise<Blob> {
  let imagen: ImageBitmap
  try {
    imagen = await createImageBitmap(archivo)
  } catch {
    throw new ErrorApi(`No pudimos leer "${archivo.name}". Probá con una foto JPG o PNG.`)
  }
  const escala = Math.min(1, LADO_MAXIMO / Math.max(imagen.width, imagen.height))
  const lienzo = document.createElement('canvas')
  lienzo.width = Math.round(imagen.width * escala)
  lienzo.height = Math.round(imagen.height * escala)
  lienzo.getContext('2d')!.drawImage(imagen, 0, 0, lienzo.width, lienzo.height)
  imagen.close()
  return new Promise((resolver, rechazar) => {
    lienzo.toBlob((blob) => (blob ? resolver(blob) : rechazar(new ErrorApi('No pudimos procesar la foto.'))), 'image/jpeg', 0.85)
  })
}

/** Sube la foto directo a Storage con una URL firmada y devuelve su URL pública. */
export async function subirFoto(archivo: File): Promise<string> {
  const blob = await achicar(archivo)
  const { url_subida, url_publica } = await api<{ url_subida: string; url_publica: string }>('/api/publicaciones/fotos', 'POST', { tipo_archivo: 'image/jpeg' })
  const respuesta = await fetch(url_subida, { method: 'PUT', headers: { 'Content-Type': 'image/jpeg' }, body: blob })
  if (!respuesta.ok) throw new ErrorApi('No pudimos subir la foto. Probá de nuevo.')
  return url_publica
}
