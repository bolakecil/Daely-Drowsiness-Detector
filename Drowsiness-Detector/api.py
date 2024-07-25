from debugpy import connect
import torch
from flask import Flask, request, jsonify
from modules import *
import firebase_admin
from firebase_admin import db, credentials
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

cred = credentials.Certificate('credentials.json')
firebase_admin.initialize_app(cred, {'databaseURL': DATABASE_URL})
ref = db.reference('/')

app = Flask(__name__)

model = load_model()
device = torch.device('cpu')    
model.to(device)

@app.route('/predict', methods=['POST'])
def predict_():
    if 'image' not in request.json:
        return jsonify({'error': 'No image provided'}), 400

    base64_string = request.json['image']
    try:
        predicted_class = predict(base64_string)
        base64_load = encode_image_to_base64('buffer.jpg')
        payload = create_payload_for_db(base64_load, predicted_class)
        ref.push(payload)
        return jsonify({'prediction': predicted_class})
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
