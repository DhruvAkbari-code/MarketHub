import asyncio

import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile, status

from core_services.config import get_settings

settings = get_settings()

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE = 5 * 1024 * 1024  # 5 MB


async def upload_image(file: UploadFile) -> dict:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Only JPEG, PNG or WEBP allowed."
        )
    data = await file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Image must be 5MB or smaller."
        )
    result = await asyncio.to_thread(
        cloudinary.uploader.upload,
        data,
        folder="markethub/products",
        resource_type="image",
    )
    return {"url": result["secure_url"], "public_id": result["public_id"]}


async def delete_image(public_id: str) -> None:
    await asyncio.to_thread(cloudinary.uploader.destroy, public_id)
