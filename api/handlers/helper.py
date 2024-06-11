import cv2
import numpy as np

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