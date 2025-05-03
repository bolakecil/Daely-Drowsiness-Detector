# modules.py
import io
import base64
from PIL import Image
from ultralytics import YOLO
from time import time
from datetime import datetime

def load_models(device):
    """
    Load YOLO models:
      - face_model: YOLOv8-face for face detection
      - classify_model: YOLOv8_face_classify for drowsiness classification
    Returns (face_model, classify_model, class_names)
    """
    # YOLO face detector weights (pretrained on faces)
    face_model = YOLO("models/yolov8n-face.pt")
    # face_model.model.to(device)

    # YOLO classification model (trained to classify active vs fatigue)
    classify_model = YOLO("models/YOLOv8 - 20 - Epochs.pt")
    # classify_model.model.to(device)

    # Map class indices to labels
    class_names = {0: 'Active Subjects', 1: 'Fatigue Subjects'}
    return face_model, classify_model, class_names


def preprocess_base64_image(base64_string: str) -> Image.Image:
    """
    Decode base64 string to PIL RGB image
    """
    image_data = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(image_data)).convert('RGB').rotate(90, expand=True)


def detect_face_and_classify(face_model, classify_model, class_names, base64_string: str):
    """
    Runs face detection with YOLO face_model; if a face is found, crops to the largest face
    and runs classification model on the cropped face. Returns (face_detected: bool, class_name: str).
    """
    # Load and run face detection
    image = preprocess_base64_image(base64_string)
    results = face_model(source=image, conf=0.25, verbose=False)
    res = results[0]
    # If no face boxes
    if not res.boxes or res.boxes.shape[0] == 0:
        return False, None

    # Run classification
    cls_results = classify_model(image, conf=0.25, verbose=False)
    cls_res = cls_results[0]

    # Top detection
    cls_id = cls_res.probs.top1
    return True, class_names.get(cls_id, str(cls_id))

def create_payload_for_db(base64_string, pred):
    """
    Returns payload (dictionary) for db
    """
    image = preprocess_base64_image(base64_string)
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    rotated_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    payload = {
        'image': rotated_b64,
        'timestamp': round(time(), 2),
        'time':{
            'year': datetime.now().strftime("%Y"),
            'month': datetime.now().strftime("%m"),
            'date': datetime.now().strftime("%d"),
            'hour': datetime.now().strftime("%H"),
            'minute': datetime.now().strftime("%M"),
            'second': datetime.now().strftime("%S")
        },
        'prediction': pred,
    }
    return payload