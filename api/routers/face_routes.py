from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from api.controller.face_controller import register_faces, known_faces
from api.models.face_model import ImageData
from api.services.face_service import generate_frames
import cv2 
import threading

router = APIRouter()

@router.post("/register")
async def register_faces_endpoint(data: ImageData):
    return await register_faces(data)

class VideoStream:
    def __init__(self, src):
        self.video_capture = cv2.VideoCapture(src)
        self.ret, self.frame = self.video_capture.read()
        self.running = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()

    def update(self):
        while self.running:
            if self.video_capture.isOpened():
                self.ret, self.frame = self.video_capture.read()

    def read(self):
        return self.ret, self.frame

    def stop(self):
        self.running = False
        self.thread.join()
        self.video_capture.release()

@router.get("/video_feed")
async def video_feed():
    video_stream = VideoStream('rtsp://admin:admin_123@192.168.29.103:554/Streaming/channels/601')
    return StreamingResponse(generate_frames(video_stream), media_type="multipart/x-mixed-replace; boundary=frame")


@router.get('/get_faces')
async def get_faces():
    return await known_faces()


