import cloudinary
import cloudinary.uploader
from app.core.config import (
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
)


def init_cloudinary():
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
    )


def upload_image(file, folder: str, public_id: str = None) -> str:
    params = {"folder": folder}
    if public_id:
        params["public_id"] = public_id
    result = cloudinary.uploader.upload(file, **params)
    return result["secure_url"]
