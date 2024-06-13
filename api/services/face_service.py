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
from api.handlers.helper import get_encodings, save_face_and_encodings

async def process_images(data):
    try:
        mongo_client = connect_to_mongo()
        redis_client = get_redis_connection()

        db = mongo_client['face_recognition']
        users_collection = db['users']

        base_folder = os.path.join('knownfaces')
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

def generate_frames():
    video_capture = cv2.VideoCapture(0)
    unknown_face_encodings = []
    unknown_face_names = []
    try:
        while True:
            ret, frame = video_capture.read()
            if not ret:
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            known_face_encodings, known_face_names = get_encodings()
            face_names = []

            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=.5) if known_face_encodings else []
                name = "Unknown"

                if True in matches:
                    best_match_index = np.argmin(face_recognition.face_distance(known_face_encodings, face_encoding))
                    name = known_face_names[best_match_index]
                else:
                    # Check against unknown faces
                    unknown_matches = face_recognition.compare_faces(unknown_face_encodings, face_encoding, tolerance=.5)
                    if True in unknown_matches:
                        best_match_index = np.argmin(face_recognition.face_distance(unknown_face_encodings, face_encoding))
                        if face_recognition.face_distance(unknown_face_encodings, face_encoding)[best_match_index] < 0.5:
                            continue
                        name = unknown_face_names[best_match_index]
                    else:
                        # Assign a new unknown identifier
                        unknown_id = len(unknown_face_encodings) + 1
                        unknown_face_encodings.append(face_encoding)
                        unknown_face_names.append(f'Unknown_{unknown_id}')
                        name = f'Unknown_{unknown_id}'
                        save_face_and_encodings(name, frame, face_encoding, len([n for n in unknown_face_names if n == name]))

                face_names.append(name)

            for (top, right, bottom, left), name in zip(face_locations, face_names):
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        video_capture.release()
        cv2.destroyAllWindows()
