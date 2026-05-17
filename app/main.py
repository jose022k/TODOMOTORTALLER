from fastapi import FastAPI
from app.core.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Todomotortaller API",
    description="Sistema Web PWA de Seguimiento y Hoja de Vida para Motos",
    version="0.1.0"
)

@app.get("/")
def root():
    return {"message": "Todomotortaller API funcionando"}