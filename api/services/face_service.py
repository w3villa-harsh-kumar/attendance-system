import base64
import numpy as np
import cv2
import os
import face_recognition
from pymongo import MongoClient
from redis import Redis
from api.handlers.helper import save_image
from config.db import connect_to_mongo
from config.redis import get_redis_connection
from api.handlers.response import format_response
from fastapi import HTTPException

async def process_images(data):
    try:
        mongo_client = connect_to_mongo()
        redis_client = get_redis_connection()

        db = mongo_client['face_recognition']
        users_collection = db['users']

        base_folder = os.path.join('saved_faces')
        user_folder = os.path.join(base_folder, data.username)
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        face_encodings_list = []  # To store face encodings
        for index, base64_image in enumerate(data.images):
            try:
                # Decode the image
                encoded_data = base64_image.split(',')[1]
                decoded_data = base64.b64decode(encoded_data)
                nparr = np.frombuffer(decoded_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                # Convert the image from BGR (OpenCV format) to RGB (face_recognition format)
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                # Detect faces in the image
                face_locations = face_recognition.face_locations(rgb_img)
                face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
                face_encodings_list.extend(face_encodings)  # Collecting encodings

                # Save the image
                img_path = os.path.join(user_folder, f"{data.username}_{index}.png")
                save_image(img_path, img)

                # Save encoding to Redis
                redis_client.set(f"{data.username}_face_{index}", face_encodings[0].tobytes())
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing image {index}: {str(e)}")

        # Save user data to MongoDB
        try:
            user_data = {
                "username": data.username,
                "images": [f"{data.username}_{i}.png" for i in range(len(data.images))],
                "encodings": [face.tobytes() for face in face_encodings_list]
            }
            users_collection.insert_one(user_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving user data to MongoDB: {str(e)}")

        return format_response(len(data.images))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing images: {str(e)}")
