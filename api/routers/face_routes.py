from fastapi import APIRouter
from api.controller.face_controller import register_faces
from api.models.face_model import ImageData

router = APIRouter()

@router.post("/register")
async def register_faces_endpoint(data: ImageData):
    return await register_faces(data)
