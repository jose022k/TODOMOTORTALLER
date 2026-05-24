from sqlalchemy import text
from app.core.database import engine, Base, SessionLocal
from app.modules.auth.models import Admin, Cliente, Mecanico
from app.modules.auth.utils import hash_password
import app.main  # This imports all routers and indirectly all models

def setup():
    # Wipe the public schema in PostgreSQL
    print("Dropping schema public cascade...")
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE;"))
        conn.execute(text("CREATE SCHEMA public;"))
        conn.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
        conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
        conn.commit()
    
    # Recreate all tables
    print("Recreating all tables...")
    Base.metadata.create_all(bind=engine)
    
    # Seed admin
    db = SessionLocal()
    try:
        admin = db.query(Admin).filter(Admin.email == "admin@todomotortaller.com").first()
        if not admin:
            new_admin = Admin(
                nombre="AdminTaller",
                email="admin@todomotortaller.com",
                contraseña=hash_password("Admintaller$")
            )
            db.add(new_admin)
            db.commit()
            print("Usuario admin creado exitosamente.")
    finally:
        db.close()
    
    print("Tablas sincronizadas con exito.")

if __name__ == "__main__":
    setup()
