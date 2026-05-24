from app.core.database import engine, SessionLocal, Base
from app.modules.auth.models import Admin, Cliente, Mecanico
from app.modules.auth.utils import hash_password

def setup():
    # Base.metadata.drop_all(bind=engine) # Opcional: Esto borraría TODO
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(Admin).filter(Admin.email == "admin@todomotortaller.com").first()
        if not admin:
            print("Creando usuario admin...")
            new_admin = Admin(
                nombre="AdminTaller",
                email="admin@todomotortaller.com",
                contraseña=hash_password("Admintaller$")
            )
            db.add(new_admin)
            db.commit()
            print("Usuario admin creado exitosamente.")
        else:
            print("El usuario admin ya existe.")
    finally:
        db.close()

if __name__ == "__main__":
    setup()
