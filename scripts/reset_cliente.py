from app.core.database import engine, Base
from app.modules.auth.models import Cliente

def setup():
    # Drop only the cliente table
    Cliente.__table__.drop(engine, checkfirst=True)
    print("Tabla cliente eliminada.")
    
    # Recreate all tables (this will recreate cliente with the new fields)
    Base.metadata.create_all(bind=engine)
    print("Tablas sincronizadas. Tabla cliente creada con los nuevos campos.")

if __name__ == "__main__":
    setup()
