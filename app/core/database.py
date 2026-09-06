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

        # Crear tabla active_session si no existe
        if "active_session" not in tables:
            conn.execute(text("""CREATE TABLE active_session (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                user_role VARCHAR(50) NOT NULL,
                token_jti VARCHAR(255) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            )"""))
            conn.commit()
        else:
            # Limpiar sesiones antiguas al iniciar el servidor
            conn.execute(text("DELETE FROM active_session"))
            conn.commit()

        # Crear tabla faq si no existe y sembrar preguntas iniciales
        if "faq" not in tables:
            conn.execute(text("""CREATE TABLE faq (
                id SERIAL PRIMARY KEY,
                servicio VARCHAR(255) NOT NULL,
                pregunta TEXT NOT NULL,
                respuesta TEXT NOT NULL,
                monto_euro FLOAT NOT NULL DEFAULT 0.0,
                es_precio_minimo BOOLEAN NOT NULL DEFAULT FALSE,
                orden INTEGER NOT NULL DEFAULT 0,
                activo BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""))
            conn.commit()

        faq_count = conn.execute(text("SELECT COUNT(*) FROM faq")).scalar()
        if faq_count == 0:
            defaults = [
                ("Costo de motor completo varillero 150 y 200 de cilindrada", "¿Cuál es el costo de reparación de un motor completo varillero 150 y 200cc?", "Costo de motor completo varillero 150 y 200 de cilindrada: 100€", 100.0, False, 1),
                ("Motor de cadena 150 y 200 de cilindrada", "¿Cuál es el precio de reparación para motor de cadena 150 y 200cc?", "Motor de cadena 150 y 200 de cilindrada: 120€", 120.0, False, 2),
                ("Medio motor varillero", "¿Cuánto cuesta la reparación de medio motor varillero?", "Medio motor varillero: 50€", 50.0, False, 3),
                ("Medio motor de cadena", "¿Cuánto cuesta la reparación de medio motor de cadena?", "Medio motor de cadena: 60€", 60.0, False, 4),
                ("Mantenimiento general moto tipo TX", "¿Cuál es el costo del mantenimiento general para moto tipo TX?", "Mantenimiento general moto tipo TX: 50€", 50.0, False, 5),
                ("Mantenimiento general moto tipo Horse", "¿Cuál es el costo del mantenimiento general para moto tipo Horse?", "Mantenimiento general moto tipo Horse: 40€", 40.0, False, 6),
                ("Cambio de relación moto de baja cilindrada", "¿Cuánto cuesta el cambio de relación para moto de baja cilindrada?", "Cambio de relación moto de baja cilindrada: 10€", 10.0, False, 7),
                ("Cambio de relación moto de media cilindrada", "¿Cuánto cuesta el cambio de relación para moto de media cilindrada?", "Cambio de relación moto de media cilindrada: 20€", 20.0, False, 8),
                ("Cambio de relación moto de alta cilindrada", "¿Cuánto cuesta el cambio de relación para moto de alta cilindrada?", "Cambio de relación moto de alta cilindrada: 30€", 30.0, False, 9),
                ("Falla eléctrica", "¿Cuál es el costo por diagnóstico y reparación de falla eléctrica?", "Falla eléctrica: mínimo 20€", 20.0, True, 10),
                ("Enderezado de chasis", "¿Cuánto cuesta el enderezado de chasis?", "Enderezado de chasis: mínimo 50€", 50.0, True, 11),
            ]
            for s, p, r, m, min_flag, o in defaults:
                conn.execute(
                    text("""INSERT INTO faq (servicio, pregunta, respuesta, monto_euro, es_precio_minimo, orden)
                            VALUES (:s, :p, :r, :m, :min_flag, :o)"""),
                    {"s": s, "p": p, "r": r, "m": m, "min_flag": min_flag, "o": o}
                )
            conn.commit()

        for table, col_def in _MIGRATIONS:
            if table not in tables:
                continue
            col_name = col_def.split()[2]
            existing = [c["name"] for c in inspector.get_columns(table)]
            if col_name not in existing:
                conn.execute(text(f"ALTER TABLE {table} {col_def}"))
                conn.commit()