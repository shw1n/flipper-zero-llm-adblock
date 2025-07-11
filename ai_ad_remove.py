import cv2
import time
import os
import asyncio
import base64
import json
from dotenv import load_dotenv
from flipper import FlipperZero
from image_classifier import classify_image_ollama, classify_image_openai
from datetime import datetime
# Load environment variables from .env file
load_dotenv()

MODEL_TO_USE = "ollama"
# MODEL_TO_USE = "openai"

# Function to classify image as ad or show
async def classify_image(image_path, model="openai"):
    with open(image_path, "rb") as image_file:
        # Encode the image in base64 format
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

    print(f"Classifying image with {model} model")
    
    if model == "openai":
        return await classify_image_openai(encoded_image)
    elif model == "ollama":
        return await classify_image_ollama(encoded_image)
    else:
        raise ValueError(f"Invalid model: {model}")

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

def get_new_run_folder():
    # Create output directory if it doesn't exist
    base_dir = "output"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    # Get list of existing run folders
    existing_runs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d.startswith("run_")]
    
    # Get next run number
    next_run = len(existing_runs)
    
    # Create new run folder with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_folder = os.path.join(base_dir, f"run_{next_run:03d}_{timestamp}")
    os.makedirs(run_folder)
    
    return run_folder

async def main():
    cap = cv2.VideoCapture(0)
    run_folder = get_new_run_folder()
    frame_count = 0
    previous_state = None
    is_muted = False  # Track whether TV is currently muted

    # list cameras
    cameras = list_cameras()
    print(f"Found {len(cameras)} cameras")
    print(f"Using camera {cameras[0]}")
    
    with FlipperZero() as flipper:
        try:
            while True:
                ret, frame = cap.read()
                if ret:
                    # Save frame with numbered filename
                    image_path = os.path.join(run_folder, f"frame_{frame_count:04d}.jpg")
                    cv2.imwrite(image_path, frame)
                    frame_count += 1
                    
                    # Classify the image
                    current_state = await classify_image(image_path, model=MODEL_TO_USE)
                    print("Current state:", current_state)
                    
                    # Send IR commands to mute/unmute AVR based on content
                    if current_state == "ad" and not is_muted:
                        flipper.send_command('vibro 1')  # Original vibro signal to mute
                        #flipper.send_command('ir tx raw 38000 0.33 275 762 271 1800 277 786 278 784 249 813 241 795 248 814 219 817 247 789 254 1818 249 1824 274 1798 279 1820 278 759 274 788 245 43887 274 789 275 1798 279 783 250 812 252 784 249 1823 274 1798 279 1820 247 1826 271 765 278 809 224 812 252 784 249 1823 275 1798 279 43880 281 782 251 1821 277 760 273 789 244 818 246 790 253 808 246 791 252 809 224 1822 275 1797 280 1819 248 1825 273 790 253 808 246')  # Send mute IR command
                        #flipper.send_command('ir tx Kaseikyo 0x325441 0x0172')
                        is_muted = True
                        print("TV muted")
                    elif current_state == "show" and is_muted:
                        flipper.send_command('vibro 0')  # Original vibro signal to unmute
                        #flipper.send_command('ir tx raw 38000 0.33 275 762 271 1800 277 786 278 784 249 813 241 795 248 814 219 817 247 789 254 1818 249 1824 274 1798 279 1820 278 759 274 788 245 43887 274 789 275 1798 279 783 250 812 252 784 249 1823 274 1798 279 1820 247 1826 271 765 278 809 224 812 252 784 249 1823 275 1798 279 43880 281 782 251 1821 277 760 273 789 244 818 246 790 253 808 246 791 252 809 224 1822 275 1797 280 1819 248 1825 273 790 253 808 246')  # Send unmute IR command
                        #flipper.send_command('ir tx Kaseikyo 0x325441 0x0172')
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
            print(f"Stopped capturing. Images saved in {run_folder}")

if __name__ == "__main__":
    asyncio.run(main())