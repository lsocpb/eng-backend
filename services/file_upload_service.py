import mimetypes

import cloudinary.uploader
from fastapi import UploadFile, HTTPException

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_image(file: UploadFile):
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type")

    mime_type, _ = mimetypes.guess_type(file.filename)
    if not mime_type or not mime_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="File size too large")


def upload_images(file_list: list[UploadFile]) -> list[str]:
    images = []

    if len(file_list) == 0:
        raise HTTPException(status_code=400, detail="No files provided")
    if len(file_list) > 3:
        raise HTTPException(status_code=400, detail="Too many files provided")

    for image in file_list:
        validate_image(image)
        result = cloudinary.uploader.upload(image.file)
        if not result.get('url'):
            raise HTTPException(status_code=500, detail="Failed to upload image")

        images.append(result.get('url'))

    return images
