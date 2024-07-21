import base64
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate('daely-drowsiness-detection-firebase-adminsdk-m97au-66db74f894.json')  # Update with the correct path to your JSON file
    firebase_admin.initialize_app(cred)

# Initialize Firestore DB
db = firestore.client()

def generate_dummy_data(num_entries):
    data = []
    current_time = datetime.now()
    
    for i in range(num_entries):
        # Generate a base64 encoded image string (dummy data)
        image_data = base64.b64encode(b'This is a dummy image').decode('utf-8')
        
        # Generate a timestamp
        timestamp = current_time - timedelta(minutes=i * 10)  # Decrease by 10 minutes for each entry
        
        # Create a dictionary with the required format
        entry = {
            'image': image_data,
            'time': {
                'year': timestamp.year,
                'month': f'{timestamp.month:02d}',
                'date': f'{timestamp.day:02d}',
                'hour': f'{timestamp.hour:02d}',
                'minute': f'{timestamp.minute:02d}',
                'second': f'{timestamp.second:02d}'
            }
        }
        
        data.append(entry)
    
    return data

def upload_to_firestore(data):
    collection_ref = db.collection('drowsiness_predictions')
    
    for entry in data:
        # Convert the entry to Firestore format
        firestore_entry = {
            'image': entry['image'],
            'timestamp': firestore.firestore.SERVER_TIMESTAMP,
            'time': entry['time']
        }
        collection_ref.add(firestore_entry)
    
    print(f"{len(data)} entries uploaded to Firestore")

# Generate 10 dummy data entries
dummy_data = generate_dummy_data(10)

# Upload the dummy data to Firestore
upload_to_firestore(dummy_data)
