from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.core.database import engine, Base, ensure_schema_updates

# Import models so SQLAlchemy discovers them for create_all
from app.modules.auth.models import Admin, Cliente, Mecanico
from app.modules.motorcycles.models import CatalogoMoto, MotoCliente, HistorialMantenimiento
from app.modules.service_orders.models import OrdenServicio, Evidencia
from app.modules.notifications.models import Notificacion
from app.modules.chat.models import Mensaje

# Import routers
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.motorcycles.router import router as motorcycles_router
from app.modules.service_orders.router import router as service_orders_router
from app.modules.notifications.router import router as notifications_router
from app.modules.reports.router import router as reports_router
from app.modules.admin.router import router as admin_router
from app.modules.chat.router import router as chat_router

Base.metadata.create_all(bind=engine)
ensure_schema_updates()

app = FastAPI(
    title="Todomotortaller API",
    description="Sistema Web PWA de Seguimiento y Hoja de Vida para Motos",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(motorcycles_router)
app.include_router(service_orders_router)
app.include_router(notifications_router)
app.include_router(reports_router)
app.include_router(admin_router)
app.include_router(chat_router)

uploads_dir = Path("uploads") / "evidencias"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def root():
    return {"message": "Todomotortaller API funcionando"}