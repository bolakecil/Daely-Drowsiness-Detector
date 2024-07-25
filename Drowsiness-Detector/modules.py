from PIL import Image
import io
import base64
from ultralytics import YOLO
from datetime import datetime
from time import time
import base64
import torch.nn as nn
import torch 
from transformers import ViTImageProcessor
from torchvision.transforms import (CenterCrop,
                                    Compose,
                                    Normalize,
                                    Resize,
                                    ToTensor)
from transformers import ViTModel

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224-in21k")
image_mean, image_std = processor.image_mean, processor.image_std
size = processor.size["height"]

normalize = Normalize(mean=image_mean, std=image_std)

_val_transforms = Compose(
        [
            Resize(size),
            CenterCrop(size),
            # ToTensor(),
            normalize,
        ]
    )

def val_transform(image):
    return _val_transforms(image)

class MetaModel(nn.Module):
    def __init__(self, vit_model, yolo_model, num_classes):
        super(MetaModel, self).__init__()
        self.vit = vit_model
        self.yolo = yolo_model.model
        self.fc = nn.Linear(4, num_classes)

    def forward(self, pixel_values, labels):
        vit_input = val_transform(pixel_values)
        vit_logits, _ = self.vit(pixel_values=vit_input, labels=labels)

        yolo_logits = self.yolo(pixel_values)

        combined_features = torch.cat((vit_logits, yolo_logits), dim=1)
        logits = self.fc(combined_features)
        return logits
    

class ViTForImageClassification(nn.Module):
    def __init__(self, num_labels=3):
        super(ViTForImageClassification, self).__init__()
        self.vit = ViTModel.from_pretrained('google/vit-base-patch16-224-in21k')
        self.dropout = nn.Dropout(0.1)
        self.classifier = nn.Linear(self.vit.config.hidden_size, num_labels)
        self.num_labels = num_labels

    def forward(self, pixel_values, labels):
        outputs = self.vit(pixel_values=pixel_values)
        output = self.dropout(outputs.last_hidden_state[:,0])
        logits = self.classifier(output)

        loss = None
        if labels is not None:
          loss_fct = nn.CrossEntropyLoss()
          loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1))
        if loss is not None:
          return logits, loss.item()
        else:
          return logits, None
    
def load_model():
    # Load ViT model
    vit_model = ViTForImageClassification(2)
    vit_model.load_state_dict(torch.load('models/ViT - patience - 5.pt', map_location=device))

    # Load YOLO model
    yolo_model = YOLO("models/YOLOv8 - 20 - Epochs.pt")
    
    meta_model = MetaModel(vit_model, yolo_model, 2)
    meta_model.load_state_dict(torch.load('models/MetaModel.pt', map_location=device))
    meta_model.to(device)
    return meta_model

def predict(base64_string):
    model = load_model()
    input_image = preprocess_base64_image(base64_string)
    results = model(ToTensor()(input_image).unsqueeze(0), None)
    _, predicted = torch.max(results, 1)
    names = [ 'Active Subjects', 'Fatigue Subjects']
    try:
        predicted_class = names[int(predicted)]
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