from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers.face_routes import router as face_router
from config.db import connect_to_mongo
from config.redis import get_redis_connection

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://localhost:5001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
app.include_router(face_router)

@app.on_event("startup")
def startup_db_client():
    connect_to_mongo()
    get_redis_connection()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Face Recognition API"}

