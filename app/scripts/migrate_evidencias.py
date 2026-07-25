import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
DATABASE_URL = os.getenv("DATABASE_URL")

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
)

engine = create_engine(DATABASE_URL)

LOCAL_BASE = os.path.join(os.path.dirname(__file__), "../../uploads/evidencias")

with engine.connect() as conn:
    result = conn.execute(
        text("SELECT id, url FROM evidencia WHERE url LIKE '/uploads/%'")
    )
    rows = result.fetchall()

    if not rows:
        print("No hay evidencias locales para migrar.")
        sys.exit(0)

    for row in rows:
        ev_id, local_url = row
        filename = os.path.basename(local_url)
        filepath = os.path.normpath(os.path.join(LOCAL_BASE, filename))

        if not os.path.exists(filepath):
            print(f"[SKIP] evidencia {ev_id}: archivo no encontrado {filepath}")
            continue

        print(f"[UPLOAD] evidencia {ev_id}: {filename} -> Cloudinary...")
        result = cloudinary.uploader.upload(
            filepath,
            folder="evidencias",
            public_id=os.path.splitext(filename)[0],
        )

        conn.execute(
            text("UPDATE evidencia SET url = :url WHERE id = :id"),
            {"url": result["secure_url"], "id": ev_id},
        )
        conn.commit()
        print(f"[OK] evidencia {ev_id}: {result['secure_url']}")

print("Migración completada.")
