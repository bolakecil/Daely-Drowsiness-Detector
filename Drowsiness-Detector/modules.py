from PIL import Image
import io
import base64
from ultralytics import YOLO
from datetime import datetime
from time import time
import base64

def load_model():
    model = YOLO("models/YOLOv8 - 20 - Epochs.pt")
    return model

def predict(base64_string):
    model = load_model()
    input_image = preprocess_base64_image(base64_string)
    results = model.predict(source=input_image,
                        save=False,
                        verbose=False)
    names = model.names
    try:
        predicted_class = names[results[0].probs.top1]
    except:
        predicted_class = 'empty'
    print(predicted_class)
    return predicted_class

def preprocess_base64_image(base64_string):
    """
    Returns image from base64 encoded image
    """
    image_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_data))
    image = image.rotate(90, expand=True)
    image.save('buffer.jpg', 'JPEG')
    return image

def encode_image_to_base64(image_path):
    """
    Encodes an image to a Base64 string.
    
    :param image_path: Path to the image file.
    :return: Base64 encoded string of the image.
    """
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        return encoded_string.decode('utf-8')
    
def create_payload_for_db(base64_string, pred):
    """
    Returns payload (dictionary) for db
    """
    payload = {
        'image': base64_string,
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