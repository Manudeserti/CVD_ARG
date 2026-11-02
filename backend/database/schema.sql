-- Esquema completo de la base de datos (PostgreSQL / Supabase).
-- Reconstruido a partir del código en noviembre 2026 porque el original solo vivía en Supabase.
-- Verificar contra Supabase (Table Editor o pg_dump --schema-only) cuando el proyecto esté activo.
-- Los tests lo usan para crear una base limpia, así que tiene que poder correrse de cero.

CREATE EXTENSION IF NOT EXISTS pgcrypto; -- gen_random_uuid()

CREATE TABLE instituciones (
    id              SERIAL PRIMARY KEY,
    nombre          VARCHAR(150) NOT NULL,
    ciudad          VARCHAR(100) NOT NULL,
    provincia       VARCHAR(100) NOT NULL DEFAULT 'Buenos Aires',
    fecha_creacion  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE usuarios (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    nombre          VARCHAR(100) NOT NULL,
    apellido        VARCHAR(100) NOT NULL,
    password_hash   TEXT NOT NULL,
    telefono        VARCHAR(20),
    rol             VARCHAR(20) NOT NULL DEFAULT 'usuario' CHECK (rol IN ('usuario', 'admin')),
    fecha_registro  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE publicaciones (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendedor_id        UUID NOT NULL REFERENCES usuarios(id),
    institucion_id     INTEGER REFERENCES instituciones(id),
    titulo             VARCHAR(100) NOT NULL,
    descripcion        TEXT,
    categoria          VARCHAR(20) NOT NULL CHECK (categoria IN ('indumentaria', 'utiles', 'libros', 'instrumentos', 'deportes')),
    talle              VARCHAR(10),
    tipo               VARCHAR(10) NOT NULL CHECK (tipo IN ('venta', 'donacion')),
    precio             NUMERIC(10, 2) NOT NULL DEFAULT 0,
    estado             VARCHAR(20) NOT NULL DEFAULT 'disponible' CHECK (estado IN ('disponible', 'reservado', 'vendido', 'baja')),
    imagenes_urls      TEXT[] NOT NULL DEFAULT '{}',
    fecha_publicacion  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE transacciones_escrow (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    publicacion_id       UUID NOT NULL REFERENCES publicaciones(id),
    comprador_id         UUID NOT NULL REFERENCES usuarios(id),
    vendedor_id          UUID NOT NULL REFERENCES usuarios(id),
    monto                NUMERIC(10, 2) NOT NULL,
    comision_plataforma  NUMERIC(10, 2) NOT NULL DEFAULT 0,
    id_pago_externo      TEXT,
    estado_pago          VARCHAR(20) NOT NULL DEFAULT 'pendiente' CHECK (estado_pago IN ('pendiente', 'retenido', 'liberado', 'cancelado', 'reembolsado')),
    qr_token             UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    fecha_creacion       TIMESTAMPTZ NOT NULL DEFAULT now(),
    fecha_liberacion     TIMESTAMPTZ
);

-- Supabase expone el esquema public en su API REST con la clave anon (que va a estar en el frontend).
-- El backend se conecta como dueño de las tablas y RLS no le aplica, así que activarlo
-- sin políticas cierra el acceso directo desde la API REST sin afectar a la app.
ALTER TABLE instituciones ENABLE ROW LEVEL SECURITY;
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE publicaciones ENABLE ROW LEVEL SECURITY;
ALTER TABLE transacciones_escrow ENABLE ROW LEVEL SECURITY;
