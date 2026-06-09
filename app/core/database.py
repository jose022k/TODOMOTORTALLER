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
]


def ensure_schema_updates():
    """Agrega columnas faltantes a tablas ya existentes (create_all no altera)."""
    with engine.connect() as conn:
        inspector = inspect(engine)
        for table, col_def in _MIGRATIONS:
            col_name = col_def.split()[2]
            existing = [c["name"] for c in inspector.get_columns(table)]
            if col_name not in existing:
                conn.execute(text(f"ALTER TABLE {table} {col_def}"))
                conn.commit()