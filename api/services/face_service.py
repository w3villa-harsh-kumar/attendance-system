import base64
import numpy as np
import cv2
import os
import face_recognition
from pymongo import MongoClient
from api.handlers.helper import save_image
from config.db import connect_to_mongo
from api.handlers.response import format_response
from fastapi import HTTPException
from api.handlers.helper import load_known_faces, load_unknown_faces
import threading
from queue import Queue
from datetime import datetime, timedelta

db_queue = Queue()
mongo_client = connect_to_mongo()

def db_worker():
    db = mongo_client["attendance"]
    known_faces_collection = db["known_faces"]
    unknown_faces_collection = db["unknown_faces"]

    while True:
        task = db_queue.get()
        if task is None:
            break
        try:
            collection, document = task
            collection.insert_one(document)
        except Exception as e:
            print(f"Error inserting document into MongoDB: {str(e)}")
        db_queue.task_done()

# Start the database worker thread
db_thread = threading.Thread(target=db_worker, daemon=True)
db_thread.start()

async def process_images(data):
    try:
        db = mongo_client['attendance']
        users_collection = db['users']

        base_folder = os.path.join('known_faces')
        user_folder = os.path.join(base_folder, data.username)
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
        replaced_username = data.username.replace(" ", "_")
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
                img_path = os.path.join(user_folder, f"{replaced_username.lower()}_{index}.jpg")
                save_image(img_path, img)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing image {index}: {str(e)}")

        # Save user data to MongoDB
        try:
            user_data = {
                "username": data.username,
                "images": [f"{data.username}_{i}.jpg" for i in range(len(data.images))],
                "encodings": [face.tobytes() for face in face_encodings_list]
            }
            users_collection.insert_one(user_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving user data to MongoDB: {str(e)}")

        return format_response(len(data.images))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing images: {str(e)}")
    
known_face_encodings, known_face_names = load_known_faces()
unknown_face_encodings, unknown_ids = load_unknown_faces()
print("unknown_face_name, ", unknown_ids)
unknown_face_counter = 0


# Dictionary to track the last seen faces and their last detected time
faces_in_previous_frame = {}

def is_new_unknown_face(face_encoding):
    if not unknown_face_encodings:
        return True
    distances = face_recognition.face_distance(unknown_face_encodings, face_encoding)
    if all(dist > 0.6 for dist in distances):  # Threshold might need adjustment
        return True
    return False

def update_faces_in_frame(face_infos):
    global faces_in_previous_frame, unknown_face_counter
    now = datetime.now()
    current_seen = set(info['name'] for info in face_infos)

    new_faces = current_seen - set(faces_in_previous_frame.keys())

    for info in face_infos:
        name, encoding, frame, top, right, bottom, left = info.values()
        if name == "Unknown" and is_new_unknown_face(encoding):
            unknown_face_encodings.append(encoding)
            unknown_face_counter += 1
            identifier = f'unknown_{unknown_face_counter}'
            unknown_ids.append(identifier)
            image_path = os.path.join('unknown_faces', f'{identifier}.jpg')
            face_image = frame[max(0, top):min(frame.shape[0], bottom), max(0, left):min(frame.shape[1], right)]
            if face_image.size > 0: 
                cv2.imwrite(image_path, face_image)
                db_queue.put((mongo_client["attendance"]["unknown_faces"], {"identifier": identifier, "timestamp": now, "event_type": "new detection"}))
                faces_in_previous_frame[identifier] = {'last_seen': now, 'identifier': identifier}
        elif name not in faces_in_previous_frame:
            faces_in_previous_frame[name] = {'last_seen': now}
        else:
            faces_in_previous_frame[name]['last_seen'] = now
    
    for face in list(faces_in_previous_frame.keys()):
        if (now - faces_in_previous_frame[face]['last_seen'] > timedelta(seconds=30)) and face not in current_seen:
            del faces_in_previous_frame[face]
            
    for face in list(new_faces):
        if face != "Unknown":
            if "unknown" in face.lower():
                image_path = os.path.join('unknown_faces', f'{face}.jpg')
                cv2.imwrite(image_path, frame)  # Save the image of the unknown face
                db_queue.put((mongo_client["attendance"]["unknown_faces"], {"identifier": f'{face}', "timestamp": now, "event_type": "new detection"}))
            else:
                db_queue.put((mongo_client["attendance"]["known_faces"], {"name": face, "timestamp": now, "event_type": "new detection"}))

def generate_frames(video_stream):
    tolerance = 0.5
    try:
        while True:
            ret, frame = video_stream.read()
            if not ret:
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            face_infos = []
            face_names = []

            for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(known_face_encodings, encoding, tolerance=tolerance)
                unknown_face_matches = face_recognition.compare_faces(unknown_face_encodings, encoding, tolerance=tolerance)

                if any(matches):
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]
                elif any(unknown_face_matches):
                    first_match_index = unknown_face_matches.index(True)
                    name = unknown_ids[first_match_index]
                else:
                    name = "Unknown"

                face_names.append(name)
                face_infos.append({
                    'name': name, 'encoding': encoding, 'frame': frame, 
                    'top': top, 'right': right, 'bottom': bottom, 'left': left
                })

            update_faces_in_frame(face_infos)

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
        video_stream.stop()

