from openai import AsyncOpenAI
import json
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Either works, just gotta set OPENAI_API_KEY in .env
client = AsyncOpenAI()

async def classify_image_openai(encoded_image) -> str:
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

def classify_image_ollama(image_path):
    pass