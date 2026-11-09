import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Navigate, Outlet, Route, Routes } from 'react-router-dom'
import './index.css'
import Bienvenida, { yaVioBienvenida } from './pages/Bienvenida'
import Catalogo from './pages/Catalogo'
import Detalle from './pages/Detalle'
import Escanear from './pages/Escanear'
import { Ingresar, Registro } from './pages/Cuenta'
import MisPublicaciones from './pages/MisPublicaciones'
import Publicar from './pages/Publicar'
import Solicitudes from './pages/Solicitudes'
import Transaccion from './pages/Transaccion'
import Transacciones from './pages/Transacciones'
import { Privada, ProveedorSesion } from './sesion'
import { MenuInferior, MenuSuperior } from './ui'

function ConMenu() {
  return (
    <>
      <MenuSuperior />
      <main className="mx-auto flex max-w-7xl flex-col gap-3.5 px-4 pt-3.5 pb-24 md:gap-5 md:px-6 md:pt-8 md:pb-12 lg:px-10">
        <Outlet />
      </main>
      <MenuInferior />
    </>
  )
}

function Inicio() {
  return yaVioBienvenida() ? <Catalogo /> : <Navigate to="/bienvenida" replace />
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ProveedorSesion>
      <BrowserRouter>
        <Routes>
          <Route path="/bienvenida" element={<Bienvenida />} />
          <Route path="/ingresar" element={<Ingresar />} />
          <Route path="/registro" element={<Registro />} />
          <Route path="/escanear" element={<Privada motivo="Para confirmar una entrega necesitás una cuenta."><Escanear /></Privada>} />
          <Route element={<ConMenu />}>
            <Route path="/" element={<Inicio />} />
            <Route path="/publicaciones/:id" element={<Detalle />} />
            <Route path="/publicar" element={<Privada motivo="Para publicar necesitás una cuenta."><Publicar /></Privada>} />
            <Route path="/mis-publicaciones" element={<Privada motivo="Para ver tus artículos necesitás una cuenta."><MisPublicaciones /></Privada>} />
            <Route path="/transacciones" element={<Privada motivo="Para ver tus operaciones necesitás una cuenta."><Transacciones /></Privada>} />
            <Route path="/transacciones/:id" element={<Privada motivo="Para ver esta operación necesitás una cuenta."><Transaccion /></Privada>} />
            <Route path="/admin/solicitudes" element={<Privada motivo="Esta sección es para administradores." soloAdmin><Solicitudes /></Privada>} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ProveedorSesion>
  </StrictMode>,
)
