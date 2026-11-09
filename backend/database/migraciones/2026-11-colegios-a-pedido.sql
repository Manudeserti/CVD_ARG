-- Alta de colegios a pedido. Correr una sola vez en Supabase (SQL Editor) antes de desplegar esta versión.
ALTER TABLE publicaciones DROP CONSTRAINT IF EXISTS publicaciones_estado_check;
ALTER TABLE publicaciones ADD CONSTRAINT publicaciones_estado_check
    CHECK (estado IN ('disponible', 'reservado', 'vendido', 'baja', 'pendiente_colegio', 'borrador'));
ALTER TABLE publicaciones ADD COLUMN aviso TEXT;

CREATE TABLE solicitudes_institucion (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    publicacion_id  UUID NOT NULL REFERENCES publicaciones(id),
    solicitante_id  UUID NOT NULL REFERENCES usuarios(id),
    nombre          VARCHAR(150) NOT NULL,
    ciudad          VARCHAR(100) NOT NULL,
    provincia       VARCHAR(100) NOT NULL,
    estado          VARCHAR(20) NOT NULL DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'aceptada', 'duplicada', 'rechazada')),
    fecha_creacion  TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE solicitudes_institucion ENABLE ROW LEVEL SECURITY;
