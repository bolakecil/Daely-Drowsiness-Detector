import torch
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import db, credentials
from dotenv import load_dotenv
import os
from modules import load_models, detect_face_and_classify, create_payload_for_db
from time import time

# Load environment and initialize Firebase
# load_dotenv()
# DATABASE_URL = os.getenv("DATABASE_URL")
# cred = credentials.Certificate('credentials.json')
# firebase_admin.initialize_app(cred, {'databaseURL': DATABASE_URL})
# ref = db.reference('/')

# Initialize Flask
app = Flask(__name__)

# Load YOLO models once
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
face_model, classify_model, class_names = load_models(device)
face_model.to(device)
classify_model.to(device)

@app.route('/print', methods=['GET'])
def printHey():
    return jsonify({"message": "Ad Hoc Works!"}), 200

@app.route('/predict', methods=['POST'])
def predict_():
    start = time()
    if 'image' not in request.json:
        return jsonify({'error': 'No image provided'}), 400

    base64_string = request.json['image']
    try:
        # Detect face and classify drowsiness in one step
        face_detected, predicted_class = detect_face_and_classify(
            face_model, classify_model, class_names, base64_string
        )
        if not face_detected:
            print("error: No face detected")
            return jsonify({'error': 'No face detected'}), 200
        
        # payload = create_payload_for_db(base64_string, predicted_class)
        # ref.push(payload)

        print("prediction", predicted_class)
        print(time() - start)
        return jsonify({'prediction': predicted_class}), 200
    except Exception as e:
        print(e)
        print(time() - start)
        return jsonify({'error': str(e)}), 500
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True) 