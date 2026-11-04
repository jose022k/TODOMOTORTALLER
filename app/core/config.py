from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "todomotortaller_production_jwt_secret_key_2026_secure_fix")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "10080"))  # 7 días

# SMTP (recuperación de contraseña)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "noreply@todomotortaller.com")

# Cloudinary
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

# Frontend
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8080")

# Tasa BCV (fuente oficial bcv.org.ve)
BCV_URL = os.getenv("BCV_URL", "https://www.bcv.org.ve/")
BCV_CACHE_MINUTES = int(os.getenv("BCV_CACHE_MINUTES", "60"))

# Web Push (VAPID)
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "s96rLYshYoBtpKmQ_V_eokwMjSKOg1VTbu_DxyaI1vg")
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "BDeomxnP5RKb75ZxkNWzOpJd6oaWKFCIpsxEojg1qW2St877bi08x2cZKs1K74SzRL1HwQcIcKU-q7CYarZ4Las")
VAPID_CLAIMS = {"sub": "mailto:admin@todomotortaller.com"}