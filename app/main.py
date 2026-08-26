import asyncio
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.database import engine, Base, ensure_schema_updates

# Import models so SQLAlchemy discovers them for create_all
from app.modules.auth.models import Admin, Cliente, Mecanico
from app.modules.motorcycles.models import CatalogoMoto, MotoCliente, HistorialMantenimiento, Marca
from app.modules.service_orders.models import OrdenServicio, Evidencia
from app.modules.notifications.models import Notificacion, PushSubscription
from app.modules.chat.models import Mensaje
from app.modules.preferences.models import UserPreference

# Import routers
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.motorcycles.router import router as motorcycles_router
from app.modules.service_orders.router import router as service_orders_router
from app.modules.notifications.router import router as notifications_router
from app.modules.reports.router import router as reports_router
from app.modules.admin.router import router as admin_router
from app.modules.chat.router import router as chat_router
from app.modules.ws.router import router as ws_router
from app.modules.bcv.router import router as bcv_router

Base.metadata.create_all(bind=engine)
ensure_schema_updates()

from app.core.cloudinary import init_cloudinary

init_cloudinary()

app = FastAPI(
    title="Todomotortaller API",
    description="Sistema Web PWA de Seguimiento y Hoja de Vida para Motos",
    version="0.1.0"
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8080")

ALLOWED_ORIGINS = [
    FRONTEND_URL,
    "http://localhost:8080",
    "http://localhost:8000",
    "http://192.168.0.194:8080",
    "https://todomotortaller-ozk4.onrender.com",
    "https://todomotortaller.onrender.com",
    "https://todomotortaller2026.onrender.com",
    "https://hilarious-shortbread-e0ccc7.netlify.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers FIRST
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(motorcycles_router)
app.include_router(service_orders_router)
app.include_router(notifications_router)
app.include_router(reports_router)
app.include_router(admin_router)
app.include_router(chat_router)
app.include_router(ws_router)
app.include_router(bcv_router)
from app.modules.preferences.router import router as preferences_router
app.include_router(preferences_router)

@app.on_event("startup")
async def startup():
    from app.core.ws_manager import init_ws
    init_ws()

# --- SERVIR FRONTEND VUE (MONOLITO) ---
DIST_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
ASSETS_DIR = os.path.join(DIST_DIR, "assets")

if os.path.isdir(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="static-assets")

@app.get("/service-worker.js")
async def service_worker():
    sw_path = os.path.join(DIST_DIR, "service-worker.js")
    if os.path.isfile(sw_path):
        response = FileResponse(sw_path, media_type="application/javascript")
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    from fastapi.responses import JSONResponse
    return JSONResponse({"error": "not found"}, status_code=404)

@app.get("/manifest.webmanifest")
async def manifest():
    path = os.path.join(DIST_DIR, "manifest.webmanifest")
    if os.path.isfile(path):
        return FileResponse(path, media_type="application/manifest+json")
    from fastapi.responses import JSONResponse
    return JSONResponse({"error": "not found"}, status_code=404)

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    file_path = os.path.join(DIST_DIR, full_path)
    if full_path and os.path.isfile(file_path):
        return FileResponse(file_path)
    index_path = os.path.join(DIST_DIR, "index.html")
    if os.path.isfile(index_path):
        response = FileResponse(index_path)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response
    from fastapi.responses import JSONResponse
    return JSONResponse({"error": "not found"}, status_code=404)
