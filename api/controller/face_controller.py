from fastapi import HTTPException
from api.models.face_model import ImageData
from api.services.face_service import process_images

async def register_faces(data: ImageData):
    try:
        response = await process_images(data)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
