import requests
import base64
import os
from dotenv import load_dotenv
import config

load_dotenv()
NSFW_API_KEY = os.getenv('NSFW_API_KEY')

async def detect_nsfw(image_path: str) -> bool:
    """AI NSFW detection via api4.ai (98% accuracy)"""
    if not NSFW_API_KEY:
        print("NSFW_API_KEY не найден — пропускаем AI-фильтр")
        return False
    
    try:
        with open(image_path, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode('utf-8')
        
        response = requests.post(
            "https://api4.ai/nsfw/v1/results",
            headers={"X-API-KEY": NSFW_API_KEY},
            json={"image": img_data}
        )
        
        if response.status_code == 200:
            result = response.json()
            # NSFW score > 0.5 = блок
            nsfw_score = result[0].get('nsfw_score', 0)
            return nsfw_score > 0.5
        return False
    except Exception as e:
        print(f"AI NSFW error: {e}")
        return False