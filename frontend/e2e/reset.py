# Deja la base de prueba local con datos para e2e/flujo.mjs. NUNCA apuntarla a Supabase: borra todo.
from pathlib import Path
import psycopg2
URL = "postgresql://postgres:test@localhost:5433/cvd_test"
schema = (Path(__file__).parents[2] / "backend" / "database" / "schema.sql").read_text(encoding="utf8")
c = psycopg2.connect(URL); c.autocommit = True; k = c.cursor()
k.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"); k.execute(schema)
k.execute("INSERT INTO instituciones (nombre, ciudad, provincia) VALUES ('Escuela 12','Mar del Plata','Buenos Aires'),('Escuela 34','Mar del Plata','Buenos Aires'),('Instituto Ejemplo','Mar del Plata','Buenos Aires'),('Colegio Sur','Tandil','Buenos Aires'),('Escuela Andina','Bariloche','Río Negro');")
k.execute("INSERT INTO usuarios (email,nombre,apellido,password_hash) VALUES ('relleno@test.com','Relleno','Test','x') RETURNING id;"); u = k.fetchone()[0]
for i in range(25):
    k.execute("INSERT INTO publicaciones (vendedor_id,institucion_id,titulo,categoria,talle,tipo,precio) VALUES (%s,2,%s,'indumentaria','8','venta',%s);", (u, f"Remera {i+1}", 1000+i))
print("base lista")
