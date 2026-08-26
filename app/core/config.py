from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_HOURS = 5

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
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
VAPID_CLAIMS = {"sub": "mailto:admin@todomotortaller.com"}