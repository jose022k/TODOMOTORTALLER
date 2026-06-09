"""
Sube logos de marcas desde una carpeta local a Cloudinary
y actualiza catalogo_moto.logo_url en la BD.

Usa el upload_preset todomotortaller_logos (unsigned upload)
como lo hace el frontend, sin necesidad de API key/secret.
"""

import os
import re
import sys
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

IMAGES_PATH = r"C:\Users\Admin\Downloads\MOTOS\logos_marcas"
CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "dorj3mvvr")
UPLOAD_PRESET = "todomotortaller_logos"
CLOUDINARY_FOLDER = "logos_marcas"


def normalize(s: str) -> str:
    s = s.upper()
    s = re.sub(r"[^A-Z0-9]", "", s)
    return s


def get_brand_map(engine) -> dict[str, str]:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT DISTINCT marca FROM catalogo_moto ORDER BY marca"))
        return {normalize(row[0]): row[0] for row in result}


def upload_logo_unsigned(filepath: str, public_id: str) -> str | None:
    url = f"https://api.cloudinary.com/v1_1/{CLOUD_NAME}/image/upload"
    with open(filepath, "rb") as f:
        files = {"file": f}
        data = {
            "upload_preset": UPLOAD_PRESET,
            "public_id": public_id,
            "folder": CLOUDINARY_FOLDER,
        }
        try:
            resp = requests.post(url, files=files, data=data, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            return result.get("secure_url")
        except Exception as e:
            print(f"Error subiendo {filepath}: {e}")
            return None


def update_logo_url(engine, marca: str, logo_url: str):
    with engine.connect() as conn:
        conn.execute(
            text("UPDATE catalogo_moto SET logo_url = :url WHERE marca = :marca"),
            {"url": logo_url, "marca": marca},
        )
        conn.commit()


def main():
    if not os.path.isdir(IMAGES_PATH):
        print(f"Error: No se encuentra la carpeta {IMAGES_PATH}")
        sys.exit(1)

    print(f"Cloudinary: {CLOUD_NAME}, preset: {UPLOAD_PRESET}")

    # Conectar BD
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL no encontrada en .env")
        sys.exit(1)
    engine = create_engine(db_url)

    # Obtener marcas
    brand_map = get_brand_map(engine)
    print(f"Marcas en BD: {len(brand_map)}")

    # Escanear imágenes
    exts = (".PNG", ".JPG", ".JPEG", ".WEBP")
    image_files = [f for f in os.listdir(IMAGES_PATH) if f.upper().endswith(exts)]
    print(f"Imagenes encontradas: {len(image_files)}")

    uploaded = 0
    skipped = 0
    not_found = []

    for filename in sorted(image_files):
        name_no_ext = os.path.splitext(filename)[0]
        normalized = normalize(name_no_ext)

        if normalized in brand_map:
            exact_brand = brand_map[normalized]
            filepath = os.path.join(IMAGES_PATH, filename)
            public_id = normalized.lower()

            print(f"\nSubiendo {filename} -> marca '{exact_brand}'...", end=" ")
            sys.stdout.flush()
            url = upload_logo_unsigned(filepath, public_id)
            if url:
                update_logo_url(engine, exact_brand, url)
                print(f"OK -> {url}")
                uploaded += 1
            else:
                print("FALLO")
        else:
            not_found.append(filename)
            skipped += 1

    print(f"\n\n--- Resumen ---")
    print(f"Subidas y actualizadas: {uploaded}")
    print(f"Omitidas (sin marca en BD): {skipped}")
    if not_found:
        print("Imagenes no coincidentes:")
        for f in not_found:
            print(f"  - {f}")


if __name__ == "__main__":
    main()
