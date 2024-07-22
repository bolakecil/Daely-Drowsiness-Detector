from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import db, credentials
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

cred = credentials.Certificate('credentials.json')
firebase_admin.initialize_app(cred, {'databaseURL': DATABASE_URL})
ref = db.reference('/')
# print(ref.get())
def get_drowsiness_data():
    outer_data = ref.get()  # Fetches everything, including the outer unique keys

    parsed_data = []
    for unique_key, data in outer_data.items():
        if isinstance(data, dict) and data.get('prediction') == 'Active Subjects':
            time_data = data.get('time')
            if time_data and all(k in time_data for k in ['year', 'month', 'date', 'hour', 'minute', 'second']):
                try:
                    timestamp = datetime(
                        int(time_data['year']),
                        int(time_data['month']),
                        int(time_data['date']),
                        int(time_data['hour']),
                        int(time_data['minute']),
                        int(time_data['second'])
                    )
                    data['timestamp'] = timestamp
                    parsed_data.append(data)
                except Exception as e:
                    print(f"Error processing data under unique key {unique_key}: {e}")
            else:
                print(f"Time data incomplete under unique key {unique_key}: {time_data}")
        else:
            if isinstance(data, dict):
                print(f"Entry under unique key {unique_key} does not match 'Fatigue' or is missing data")

    if not parsed_data:
        print("No matching 'Fatigue' records found or timestamp parsing failed.")
    else:
        print(f"Parsed data with timestamp: {parsed_data[:5]}")

    return parsed_data

parsed_drowsiness_data = get_drowsiness_data()
print(parsed_drowsiness_data)
