import cv2
import numpy as np
import os
from config.redis import get_redis_connection

def save_image(img_path, img):
    try:
        cv2.imwrite(img_path, img)
    except Exception as e:
        raise Exception(f"Error saving image: {str(e)}")


def load_face_encodings(users_collection):
  try:
    users = users_collection.find({})
    face_encodings = []
    for user in users:
        for encoding in user['encodings']:
            face_encodings.append(np.frombuffer(encoding, dtype=np.float64))
    return face_encodings
  except Exception as e:
        raise Exception(f"Error in finding encodings: {str(e)}")
      
# Utility to get encodings from Redis
def get_encodings():
    redis_client = get_redis_connection()
    keys = redis_client.keys('*_encodings')
    known_face_encodings = []
    known_face_names = []

    for key in keys:
        name = key.decode('utf-8').replace('_encodings', '')
        stored_encodings = redis_client.hgetall(key)

        for field_name, encoding_bytes in stored_encodings.items():
            encoding = np.frombuffer(encoding_bytes, dtype=np.float64)
            known_face_encodings.append(encoding)
            known_face_names.append(name)

    return known_face_encodings, known_face_names
  
# Save faces and encodings in Redis
def save_face_and_encodings(name, frame, face_encoding, count):
    redis_client = get_redis_connection()
    user_folder = f'knownfaces/{name}'
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    image_path = os.path.join(user_folder, f'{name}_{count}.jpg')
    cv2.imwrite(image_path, frame)
    print(f'Image saved as {image_path}')

    encoding_key = f'{name}_encodings'
    field_name = f'encoding_{count}'
    redis_client.hset(encoding_key, field_name, face_encoding.tobytes())
    print(f'Encoding saved in Redis hash with key {encoding_key} and field {field_name}')


def serialize_face(face):
    base_server_url = "http://localhost:8000"
    return {
        "id": str(face["_id"]),
        "username": face.get("username", "N/A"), 
        "images": face.get("images", []), 
        # "image_path": f"{base_server_url}/{face.get('image_path', 'default.jpg')}", 
    }