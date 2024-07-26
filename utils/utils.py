from db_management.database import SessionLocal
from fastapi import UploadFile, HTTPException
import mimetypes

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
