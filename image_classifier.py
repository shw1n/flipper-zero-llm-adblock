from openai import AsyncOpenAI
import json
from dotenv import load_dotenv
import requests

from ollama import chat, ChatResponse
from ollama import AsyncClient as AsyncOllama


# Load environment variables from .env file
load_dotenv()

# Either works, just gotta set OPENAI_API_KEY in .env
# openai_client = AsyncOpenAI()
# ollama_client = AsyncOllama()
#PROMPT = "Return whether the image on the TV is an ad or not in JSON format (e.g., {'content': 'ad'} or {'content': 'show'}). If not sure or don't see a TV, just take best guess. Do not say anything else but the requested JSON, or you will be penalized. Note: do NOT start text with ```json"
PROMPT = "Return whether the image on the TV is an ad or not in JSON format (e.g., {'content': 'ad'} or {'content': 'show'}). Do not say anything else but the requested JSON, or you will be penalized. Note: do NOT start text with ```json"

# Add a flag to track if system prompt has been set
system_prompt_set = False

async def classify_image_openai(encoded_image) -> str:
    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
            "role": "user", 
            "content": [
                {
                "type": "text",
                "text": PROMPT,
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

async def classify_image_ollama(encoded_image):
    global system_prompt_set
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": "llama3.2-vision:flipper",
        #"model": "moondream",
        "prompt": "Analyze this image as per system instructions",
        "images": [encoded_image],
        "stream": False,
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise exception for bad status codes

        print(response.content)
        
        # Print raw response for debugging
        raw_content = response.json()["response"]
        print(f"Raw response: {raw_content}")
        
        # Clean up the response if needed
        cleaned_content = raw_content.strip().replace("'", '"')
        response_json = json.loads(cleaned_content)
        return response_json['content']
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Failed to parse: {raw_content}")
        return "unknown"
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return "unknown"
