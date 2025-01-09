import cv2
import time
import os
#import requests
import base64
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to classify image as AD or SHOW
def classify_image(image_path):
    with open(image_path, "rb") as image_file:
        # Encode the image in base64 format
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Replace with your OpenAI endpoint and API key
    url = "https://api.openai.com/v1/your_image_classification_model_endpoint"
    headers = {
        "Authorization": os.getenv("OPENAI_API_KEY"),
        "Content-Type": "application/json",
    }
    data = {
        "image": encoded_image,
        # Additional params for classification (if any)
    }
    
    # Send the request to OpenAI
    #response = requests.post(url, headers=headers, json=data)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": "Return whether the image on the TV is an ad or not in JSON format (e.g., {'content': 'AD'} or {'content': 'SHOW'}).",
                },
                {
                "type": "image_url",
                "image_url": {
                    "url":  f"data:image/jpeg;base64,{encoded_image}"
                },
                },
            ],
            }
        ],
    )

    print(response.choices[0])

# Initialize webcam capture
cap = cv2.VideoCapture(0)

try:
    while True:
        # Capture frame-by-frame
        print("Capturing frame")
        ret, frame = cap.read()
        print("Frame captured")
        if ret:
            # Save the captured frame as a temporary image file
            image_path = "temp_image.jpg"
            cv2.imwrite(image_path, frame)
            
            # Classify the image
            state = classify_image(image_path)
            print("Current state:", state)
        
        # Wait for 3 seconds
        time.sleep(3)

except KeyboardInterrupt:
    # Release the capture when done
    cap.release()
    print("Stopped capturing images.")