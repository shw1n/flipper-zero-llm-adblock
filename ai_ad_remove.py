import cv2
import time
import os
import asyncio
import base64
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI
from flipper import FlipperZero

# Load environment variables from .env file
load_dotenv()

# Either works, just gotta set OPENAI_API_KEY in .env
client = AsyncOpenAI()

# Function to classify image as ad or show
async def classify_image(image_path):
    with open(image_path, "rb") as image_file:
        # Encode the image in base64 format
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
            "role": "user", 
            "content": [
                {
                "type": "text",
                "text": "Return whether the image on the TV is an ad or not in JSON format (e.g., {'content': 'ad'} or {'content': 'show'}). Note: do NOT start text with ```json",
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encoded_image}"
                },
                },
            ],
            }
        ],
    )

    print(response.choices[0])
    try:
        # Print raw response for debugging
        raw_content = response.choices[0].message.content
        print(f"Raw response: {raw_content}")
        
        # Clean up the response if needed
        cleaned_content = raw_content.strip().replace("'", '"')
        response_json = json.loads(cleaned_content)
        return response_json['content']
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Failed to parse: {raw_content}")
        return "unknown"

# List all available cameras
def list_cameras():
    available_cameras = []
    for i in range(10):  # Check first 10 indexes
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"Camera index {i} is available")
            available_cameras.append(i)
        cap.release()
    return available_cameras

# Test specific camera
def test_camera(camera_index):
    print(f"\nTesting camera {camera_index}...")
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"Failed to open camera {camera_index}")
        return False
    
    print("Camera opened successfully")
    print(f"Resolution: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
    
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        cap.release()
        return False
    
    print("Successfully grabbed frame")
    try:
        cv2.imwrite(f'test_camera_{camera_index}.jpg', frame)
        print(f"Successfully saved test_camera_{camera_index}.jpg")
    except Exception as e:
        print(f"Failed to save image: {e}")
    
    cap.release()
    return True

# print("Searching for available cameras...")
# cameras = list_cameras()

# if not cameras:
#     print("No cameras found!")
# else:
#     print(f"\nFound {len(cameras)} camera(s)")
#     for cam in cameras:
#         test_camera(cam)

async def main():
    cap = cv2.VideoCapture(1)
    previous_state = None
    is_muted = False  # Track whether TV is currently muted
    
    # Initialize Flipper Zero connection
    with FlipperZero() as flipper:
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
                    current_state = await classify_image(image_path)
                    print("Current state:", current_state)
                    
                    # Send IR commands to mute/unmute AVR based on content
                    if current_state == "ad" and not is_muted:
                        # flipper.send_command('vibro 1')  # Original vibro signal to mute
                        #flipper.send_command('ir tx raw 38000 0.33 275 762 271 1800 277 786 278 784 249 813 241 795 248 814 219 817 247 789 254 1818 249 1824 274 1798 279 1820 278 759 274 788 245 43887 274 789 275 1798 279 783 250 812 252 784 249 1823 274 1798 279 1820 247 1826 271 765 278 809 224 812 252 784 249 1823 275 1798 279 43880 281 782 251 1821 277 760 273 789 244 818 246 790 253 808 246 791 252 809 224 1822 275 1797 280 1819 248 1825 273 790 253 808 246')  # Send mute IR command
                        flipper.send_command('ir tx Kaseikyo 0x325441 0x0172')
                        is_muted = True
                        print("TV muted")
                    elif current_state == "show" and is_muted:
                        # flipper.send_command('vibro 0')  # Original vibro signal to unmute
                        #flipper.send_command('ir tx raw 38000 0.33 275 762 271 1800 277 786 278 784 249 813 241 795 248 814 219 817 247 789 254 1818 249 1824 274 1798 279 1820 278 759 274 788 245 43887 274 789 275 1798 279 783 250 812 252 784 249 1823 274 1798 279 1820 247 1826 271 765 278 809 224 812 252 784 249 1823 275 1798 279 43880 281 782 251 1821 277 760 273 789 244 818 246 790 253 808 246 791 252 809 224 1822 275 1797 280 1819 248 1825 273 790 253 808 246')  # Send unmute IR command
                        flipper.send_command('ir tx Kaseikyo 0x325441 0x0172')
                        is_muted = False
                        print("TV unmuted")
                    
                    previous_state = current_state
                
                # Wait for 3 seconds
                time.sleep(3)
        except KeyboardInterrupt:
            # Make sure TV is unmuted when exiting
            if is_muted:
                pass
                # flipper.send_command('vibro 0')  # Original vibro signal to unmute
                #flipper.send_command('ir tx /ext/infrared/AVR_Unmute.ir')
            # Release the capture when done
            cap.release()
            print("Stopped capturing images.")

if __name__ == "__main__":
    asyncio.run(main())