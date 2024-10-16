from fastapi import APIRouter, UploadFile, File
from starlette import status

import services.file_upload_service

router = APIRouter(
    prefix="/image",
    tags=["image"]
)


@router.put(path="", status_code=status.HTTP_201_CREATED)
async def upload_image(file: UploadFile = File(...)):
    return {"url": services.file_upload_service.upload_image(file)}
