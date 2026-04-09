import os
import logging
import requests
from google import genai
from google.genai import types  
from datetime import datetime, timezone
from PIL import Image
from io import BytesIO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
MEDIA_LIMIT = int(os.getenv("MEDIA_LIMIT", "15"))

gemini_client = None
if GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
else:
    logger.error("GEMINI_API_KEY not set")

def download_whatsapp_media(media_id, return_mime=False):
    if not WHATSAPP_TOKEN:
        logger.error("WHATSAPP_TOKEN not set")
        return (None, None) if return_mime else None
    
    try:
        #get the temporary media URL from Meta
        url = f"https://graph.facebook.com/v21.0/{media_id}"
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        media_data = response.json()
        media_url = media_data.get("url")
        mime_type = media_data.get("mime_type", "")
        
        
        
        
        
        
        
        #check media size before downloading limit to 5MB
        file_size = media_data.get("file_size", 0)
        max_size_bytes = 5 * 1024 * 1024  #5MB
        
        if file_size > max_size_bytes:
            logger.warning(f"Media size {file_size} exceeds 5MB limit.")
            return (None, None) if return_mime else None
        
        #download the actual binary file
        media_response = requests.get(media_url, headers=headers)
        media_response.raise_for_status()
        
        if return_mime:
            return media_response.content, mime_type
        return media_response.content
    except Exception as e:
        logger.error(f"Error downloading WhatsApp media: {e}")
        return (None, None) if return_mime else None

def get_media_part(media_id):
   #downloads media from WhatsApp and returns a gemini Part object for 
    media_content, mime_type = download_whatsapp_media(media_id, return_mime=True)
    if not media_content:
        return None
        
    if not mime_type:
        mime_type = 'application/octet-stream'
        
    try:
        return types.Part.from_bytes(data=media_content, mime_type=mime_type)
    except Exception as e:
        logger.error(f"Error creating Part from media: {e}")
        return None

def check_media_rate_limit(user_id, db_collection):
   
    #Check if the user has reached their daily media quota.
    if db_collection is None:
        return True 

    #start of the current day in UTC
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    
    count = db_collection.count_documents({
        "user_id": user_id,
        "message_type": {"$in": ["image", "document"]},
        "timestamp": {"$gte": today}
    })
    
    return count < MEDIA_LIMIT