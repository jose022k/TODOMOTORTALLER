from fastapi import FastAPI
from app.core.database import engine, Base

# Import routers
from app.modules.auth.router import router as auth_router
from app.modules.clients.router import router as clients_router
from app.modules.motorcycles.router import router as motorcycles_router
from app.modules.service_orders.router import router as service_orders_router
from app.modules.notifications.router import router as notifications_router
from app.modules.reports.router import router as reports_router
from app.modules.mechanics.router import router as mechanics_router
from app.modules.admin.router import router as admin_router
from app.modules.chat.router import router as chat_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Todomotortaller API",
    description="Sistema Web PWA de Seguimiento y Hoja de Vida para Motos",
    version="0.1.0"
)

# Include routers
app.include_router(auth_router)
app.include_router(clients_router)
app.include_router(motorcycles_router)
app.include_router(service_orders_router)
app.include_router(notifications_router)
app.include_router(reports_router)
app.include_router(mechanics_router)
app.include_router(admin_router)
app.include_router(chat_router)

@app.get("/")
def root():
    return {"message": "Todomotortaller API funcionando"}