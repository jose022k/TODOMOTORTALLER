from app.core.database import SessionLocal
from app.modules.auth.models import User
from app.modules.auth.utils import hash_password

db = SessionLocal()
try:
    admin_email = "admin@todomotortaller.com"
    admin = db.query(User).filter(User.email == admin_email).first()
    
    if not admin:
        print("Creating default admin user...")
        new_admin = User(
            nombre="Admintodomotortaller",
            email=admin_email,
            contraseña=hash_password("Admintaller$"),
            rol="admin"
        )
        db.add(new_admin)
        db.commit()
        print("Admin user created successfully!")
    else:
        print("Admin user already exists.")
except Exception as e:
    print(f"Error creating admin: {e}")
finally:
    db.close()
