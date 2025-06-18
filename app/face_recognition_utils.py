import os
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import base64
from database import save_face_image, get_face_images, save_face_encoding, get_face_encoding, is_face_recognition_enabled

# Create directory for storing face images
FACE_IMAGES_DIR = os.path.join('app', 'face_images')
os.makedirs(FACE_IMAGES_DIR, exist_ok=True)

# Load OpenCV's pre-trained face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def process_base64_image(base64_image):
    """Process a base64 encoded image and return a numpy array"""
    # Remove the data URL prefix if present
    if ',' in base64_image:
        base64_image = base64_image.split(',')[1]

    # Decode base64 string to bytes
    image_bytes = base64.b64decode(base64_image)

    # Convert bytes to numpy array
    image = Image.open(BytesIO(image_bytes))
    return np.array(image)

def detect_faces(image):
    """Detect faces in an image and return face locations"""
    # Convert image to grayscale for face detection
    if len(image.shape) == 3:
        if image.shape[2] == 4:  # If image has alpha channel
            image_rgb = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        else:
            image_rgb = image
        gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    else:
        gray = image

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    # Convert to format (top, right, bottom, left) to match original API
    face_locations = []
    for (x, y, w, h) in faces:
        face_locations.append((y, x+w, y+h, x))

    return face_locations

def extract_face_features(image, face_location=None):
    """Extract features from a face in an image using OpenCV"""
    # If face location is provided, use it, otherwise detect faces
    if face_location is None:
        face_locations = detect_faces(image)
        if not face_locations:
            return None
        face_location = face_locations[0]  # Use the first face

    # Extract the face region
    top, right, bottom, left = face_location
    face_image = image[top:bottom, left:right]

    # Resize to a standard size
    face_image = cv2.resize(face_image, (100, 100))

    # Convert to grayscale
    if len(face_image.shape) == 3:
        face_image = cv2.cvtColor(face_image, cv2.COLOR_RGB2GRAY)

    # Flatten the image to create a feature vector
    face_features = face_image.flatten()

    # Normalize the features
    face_features = face_features / 255.0

    return face_features

def save_training_image(user_id, base64_image):
    """Save a training image for a user"""
    try:
        # Process the base64 image
        image = process_base64_image(base64_image)

        # Detect faces in the image
        face_locations = detect_faces(image)

        if not face_locations:
            return {"success": False, "message": "No face detected in the image"}

        # Convert image to bytes for storage
        pil_image = Image.fromarray(image)
        img_byte_arr = BytesIO()
        pil_image.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        # Save the image to the database
        save_face_image(user_id, img_byte_arr)

        return {"success": True, "message": "Face image saved successfully"}
    except Exception as e:
        return {"success": False, "message": f"Error saving face image: {str(e)}"}

def train_face_model(user_id):
    """Train the face recognition model for a user"""
    try:
        # Get all training images for the user
        face_images = get_face_images(user_id)

        if not face_images:
            return {"success": False, "message": "No training images found for the user"}

        # Process each image and extract face features
        face_features_list = []
        for face_image in face_images:
            # Convert bytes to image
            image_bytes = face_image['image_data']
            image = Image.open(BytesIO(image_bytes))
            image_array = np.array(image)

            # Detect faces and extract features
            face_locations = detect_faces(image_array)
            if face_locations:
                features = extract_face_features(image_array, face_locations[0])
                if features is not None:
                    face_features_list.append(features)

        if not face_features_list:
            return {"success": False, "message": "No valid faces found in training images"}

        # Calculate the average face features
        average_features = np.mean(face_features_list, axis=0)

        # Save the face features to the database
        save_face_encoding(user_id, average_features)

        return {"success": True, "message": "Face recognition model trained successfully"}
    except Exception as e:
        return {"success": False, "message": f"Error training face model: {str(e)}"}

def verify_face(user_id, base64_image, similarity_threshold=0.8):
    """Verify a face against the stored features for a user"""
    try:
        # Check if face recognition is enabled for the user
        if not is_face_recognition_enabled(user_id):
            return {"success": False, "message": "Face recognition not enabled for this user"}

        # Get the stored face features for the user
        stored_features = get_face_encoding(user_id)
        if stored_features is None:
            return {"success": False, "message": "No face features found for this user"}

        # Process the base64 image
        image = process_base64_image(base64_image)

        # Detect faces in the image
        face_locations = detect_faces(image)

        if not face_locations:
            return {"success": False, "message": "No face detected in the image"}

        # Extract features from the first face
        face_features = extract_face_features(image, face_locations[0])

        if face_features is None:
            return {"success": False, "message": "Failed to extract face features"}

        # Compare the face features with the stored features using cosine similarity
        stored_features_array = np.array(stored_features)
        similarity = np.dot(face_features, stored_features_array) / (np.linalg.norm(face_features) * np.linalg.norm(stored_features_array))

        if similarity >= similarity_threshold:
            return {"success": True, "message": "Face verification successful"}
        else:
            return {"success": False, "message": "Face verification failed"}
    except Exception as e:
        return {"success": False, "message": f"Error verifying face: {str(e)}"}
