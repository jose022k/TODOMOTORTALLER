from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


_MIGRATIONS = [
    ("cliente", "ADD COLUMN IF NOT EXISTS activo BOOLEAN NOT NULL DEFAULT TRUE"),
    ("mecanico", "ADD COLUMN IF NOT EXISTS activo BOOLEAN NOT NULL DEFAULT TRUE"),
    ("catalogo_moto", "ADD COLUMN IF NOT EXISTS logo_url TEXT"),
    ("moto_cliente", "ADD COLUMN IF NOT EXISTS color VARCHAR(50)"),
    ("mensaje", "ADD COLUMN IF NOT EXISTS editado BOOLEAN NOT NULL DEFAULT FALSE"),
    ("mensaje", "ADD COLUMN IF NOT EXISTS fecha_edicion TIMESTAMP"),
    ("orden_servicio", "ADD COLUMN IF NOT EXISTS monto FLOAT"),
    ("orden_servicio", "ADD COLUMN IF NOT EXISTS moneda VARCHAR(3)"),
    ("orden_servicio", "ADD COLUMN IF NOT EXISTS tasa_bcv FLOAT"),
    ("orden_servicio", "ADD COLUMN IF NOT EXISTS monto_usd FLOAT"),
]


def ensure_schema_updates():
    """Agrega columnas faltantes y crea tablas nuevas."""
    with engine.connect() as conn:
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        # Recrear push_subscription si existe con columnas incorrectas
        if "push_subscription" in tables:
            cols = [c["name"] for c in inspector.get_columns("push_subscription")]
            if "p256dh_key" in cols or "id_cliente" in cols:
                conn.execute(text("DROP TABLE push_subscription CASCADE"))
                conn.commit()
                inspector = inspect(engine)
                tables = inspector.get_table_names()

        if "push_subscription" not in tables:
            conn.execute(text("""CREATE TABLE push_subscription (
                id SERIAL PRIMARY KEY,
                endpoint TEXT NOT NULL UNIQUE,
                p256dh TEXT NOT NULL,
                auth TEXT NOT NULL,
                admin_id INTEGER REFERENCES admin(id),
                cliente_id INTEGER REFERENCES cliente(id),
                mecanico_id INTEGER REFERENCES mecanico(id)
            )"""))
            conn.commit()

        # Crear tabla marca si no existe
        if "marca" not in tables:
            conn.execute(text("""CREATE TABLE marca (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL UNIQUE,
                logo_url TEXT
            )"""))
            conn.commit()

        # Poblar desde marcas existentes en catalogo_moto (siempre, por si create_all ya la creó)
        existing = conn.execute(
            text("SELECT DISTINCT marca, logo_url FROM catalogo_moto")
        ).fetchall()
        for row in existing:
            nm = row._mapping["marca"]
            lu = row._mapping["logo_url"]
            conn.execute(
                text("INSERT INTO marca (nombre, logo_url) VALUES (:n, :l) ON CONFLICT (nombre) DO NOTHING"),
                {"n": nm, "l": lu}
            )
        conn.commit()

        # Crear tabla user_preference si no existe
        if "user_preference" not in tables:
            conn.execute(text("""CREATE TABLE user_preference (
                id SERIAL PRIMARY KEY,
                user_role VARCHAR(20) NOT NULL,
                user_id INTEGER NOT NULL,
                notify_messages BOOLEAN NOT NULL DEFAULT TRUE,
                notify_orders BOOLEAN NOT NULL DEFAULT TRUE,
                dark_mode BOOLEAN NOT NULL DEFAULT FALSE,
                UNIQUE (user_role, user_id)
            )"""))
            conn.commit()

        # Crear tabla configuracion (clave-valor) si no existe
        if "configuracion" not in tables:
            conn.execute(text("""CREATE TABLE configuracion (
                clave VARCHAR(100) PRIMARY KEY,
                valor TEXT
            )"""))
            conn.commit()

        for table, col_def in _MIGRATIONS:
            if table not in tables:
                continue
            col_name = col_def.split()[2]
            existing = [c["name"] for c in inspector.get_columns(table)]
            if col_name not in existing:
                conn.execute(text(f"ALTER TABLE {table} {col_def}"))
                conn.commit()