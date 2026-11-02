-- Cambios del Sprint A sobre la base existente en Supabase.
-- Correr en el SQL Editor de Supabase una sola vez.
-- Supone que los CHECK tienen el nombre que Postgres les pone por defecto; si falla,
-- buscar el nombre real en Table Editor > publicaciones > Constraints.

-- Nuevo estado 'baja' para que el vendedor pueda retirar una publicación sin borrar su historial.
ALTER TABLE publicaciones DROP CONSTRAINT IF EXISTS publicaciones_estado_check;
ALTER TABLE publicaciones ADD CONSTRAINT publicaciones_estado_check
    CHECK (estado IN ('disponible', 'reservado', 'vendido', 'baja'));

-- Para dar permisos de administrador (gestión de instituciones):
-- UPDATE usuarios SET rol = 'admin' WHERE email = 'tu-correo@ejemplo.com';
