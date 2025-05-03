import requests
import base64

# Read and encode the image
with open('test_bang.png', 'rb') as img_file:
    b64_image = base64.b64encode(img_file.read()).decode('utf-8')

# Prepare the payload
payload = {
    'image': f'{b64_image}'
}

# Send the POST request
response = requests.post('http://192.168.50.1:8888/predict', json=payload)

# Print the response
print(response.status_code)
print(response.json())