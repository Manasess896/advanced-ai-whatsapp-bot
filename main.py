import os
from dotenv import load_dotenv
load_dotenv(override=True)  
import requests
import logging
import json
from flask import Flask, request, jsonify
from google import genai
from google.genai import types
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from datetime import datetime, timezone
import traceback
import uuid
import media
import threading
from user_profile import update_user_profile_in_background
from fallback import generate_fallback_reply_with_context

app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

GROQ_API_KEY = os.getenv("GROQ_API_KEY") # No longer needed

MONGO_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")#import collection for storing the conversations this is set in .env file 
LOCATION_COLLECTION_NAME = "user_locations"  # a collection for storing location data i made a matsake this collection also saves user conversations in the future i will saparate them 

BOT_NAME = os.getenv("BOT_NAME")
CREATOR_NAME = os.getenv("CREATOR_NAME")
CREATOR_EMAIL = os.getenv("CREATOR_EMAIL")  
CREATOR_WHATSAPP = os.getenv("CREATOR_WHATSAPP")
PRIVACY_URL = os.getenv("PRIVACY_URL")
TERMS_URL = os.getenv("TERMS_URL")
MEMORY_LIMIT = int(os.getenv("MEMORY_LIMIT", "4"))  # Drastically reduced for background profile usage

ERROR_MESSAGES = {
    "ERR100": "I encountered a problem when processing your request. Please tell the developer: ERR100.",
    "ERR200": "I encountered a problem when processing your request. Please tell the developer: ERR200.",
    "ERR300": "I encountered a problem when processing your request. Please tell the developer: ERR300.",
    "ERR400": "AI service is unavailable. Please try again later. (ERR400)"
}

def dev_log(exc: Exception, code: str):
  
    logging.error("Developer error %s: %s", code, exc)
    logging.error(traceback.format_exc())

#start AI cervice
ai_client = media.gemini_client
if ai_client:
    logging.info("200 AI service ready (Gemini)")
else:
    logging.error("No Gemini API key configured in media")

mongo_client = None
db = None
collection = None
location_collection = None
country_codes = []


try:
    with open('codes.json', 'r', encoding='utf-8') as f:
        country_codes = json.load(f)
except Exception as e:
    logging.error("Could not load codes.json: %s", e)
    country_codes = []

if MONGO_URI:
    try:
        mongo_client = MongoClient(
            MONGO_URI, 
            serverSelectionTimeoutMS=15000,  
            connectTimeoutMS=15000,
            socketTimeoutMS=15000,
            maxPoolSize=10,
            retryWrites=True
        )
        
        #test   the connection
        mongo_client.admin.command('ping')
        db = mongo_client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        location_collection = db[LOCATION_COLLECTION_NAME]  # Initialize location collection
        logging.info("200 Database connected")
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        dev_log(e, "ERRDB_CONN")
        logging.error("MongoDB connection failed; memory and location features disabled.")
        collection = None
        location_collection = None
    except Exception as e:
        dev_log(e, "ERRDB_CONN")
        logging.error("MongoDB connection error; memory and location features disabled.")
        collection = None
        location_collection = None
else:
    logging.warning("MONGO_URI not set; memory features disabled.")


def make_user_safe_error(code_key: str) -> str:
    #return a short message for the user while logging details to dev logs
    return ERROR_MESSAGES.get(code_key, "An error occurred. Please inform the developer.")

def detect_user_location(phone_number: str) -> dict | None:
    #detect user's country and location based on phone number using country codes
    if not country_codes or not phone_number:
        return None
    
    # rrmove any non-digit characters from phone number
    clean_phone = ''.join(filter(str.isdigit, phone_number))
    
    if not clean_phone:
        return None
    
    # try to match country codes (sorted by length descending to match longer codes first)
    sorted_codes = sorted(country_codes, key=lambda x: len(x['dial_code'].replace('-', '')), reverse=True)
    
    for country in sorted_codes:
        dial_code = country['dial_code'].replace('-', '')  # Remove hyphens for matching
        
        # check if phone number starts with this country code
        if clean_phone.startswith(dial_code):
            return {
                'country_name': country['name'],
                'country_code': country['code'],
                'dial_code': country['dial_code'],
                'phone_number': phone_number,
                'clean_phone': clean_phone,
                'detected_at': datetime.now(timezone.utc),
                'mobile_number_length': country.get('mobile_number_length')
            }
    
    return None

def save_user_location(user_id: str, location_data: dict, user_name: str = None) -> bool:
    #save or update user location data in the location collection
    if location_collection is None:
        logging.info("Location collection disabled, skipping location save.")
        return False
    
    try:
        # Cceck if user location already exists
        existing_location = location_collection.find_one({"user_id": user_id})
        #set user doc in db
        location_doc = {
            "user_id": user_id,
            "user_name": user_name,
            "country_name": location_data['country_name'],
            "country_code": location_data['country_code'],
            "dial_code": location_data['dial_code'],
            "phone_number": location_data['phone_number'],
            "clean_phone": location_data['clean_phone'],
            "mobile_number_length": location_data.get('mobile_number_length'),
            "first_detected": location_data['detected_at'] if not existing_location else existing_location.get('first_detected', location_data['detected_at']),
            "last_updated": datetime.now(timezone.utc),
            "detection_count": (existing_location.get('detection_count', 0) + 1) if existing_location else 1
        }
        
        if existing_location:
            #update existing location 
            location_collection.update_one(
                {"user_id": user_id},
                {"$set": location_doc}
            )
        else:
            #insert new location if has non
            location_collection.insert_one(location_doc)
        
        logging.info("200 Location extracted")
        
        return True
        
    except Exception as e:
        dev_log(e, "ERR_LOCATION_SAVE")
        logging.error("Failed to save location for user %s", user_id[-4:])
        return False

def get_user_location(user_id: str) -> dict | None:
    """Get user's stored location data."""
    if location_collection is None:
        return None
    
    try:
        location_data = location_collection.find_one({"user_id": user_id})
        if location_data:
            return location_data
        return None
    except Exception as e:
        dev_log(e, "ERR_LOCATION_GET")
        return None

def send_message(to: str, text: str) -> bool:
   #Send a text message via whatsApp cloud API returns True on success
    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        logging.error("WhatsApp token or phone id missing.")
        return False

    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        if r.status_code >= 400:
            logging.error("WhatsApp API error: %s", r.text)
            return False
        logging.info("200 Sent message to WhatsApp API")
        return True
    except Exception as e:
        dev_log(e, "ERR_WAPP_SEND")
        return False

def save_message_to_db(user_id: str, message: str, sender_type: str, message_type: str = "text", 
                       user_name: str | None = None, phone_number: str | None = None) -> bool:
   
    if collection is None:
        logging.info("DB disabled, skipping save.")
        return False

    try:
        doc = {
            "user_id": user_id,              
            "message": message,              
            "sender_type": sender_type,      
            "message_type": message_type,    
            "timestamp": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "user_name": user_name,          
            "phone_number": phone_number,   
            "conversation_id": f"chat_{user_id}",  
        }
        
        result = collection.insert_one(doc)
        logging.info("200 Saved message to database")
        return True
        
    except Exception as e:
        dev_log(e, "ERR100")
        logging.error("Failed to save message for user %s", user_id)
        return False

def get_conversation_history(user_id: str, limit: int | None = None) -> list:
  
    if collection is None:
        logging.info("DB disabled: returning empty history.")
        return []

    try:
        actual_limit = limit or MEMORY_LIMIT
        
        
        query = {
            "user_id": user_id,  
            "conversation_id": f"chat_{user_id}"  
        }
        
        cursor = collection.find(query).sort("timestamp", -1).limit(actual_limit)
        records = list(cursor)
       
        history = []
        for r in reversed(records):
          
            if r.get("user_id") == user_id:
                history.append({
                    "sender_type": r.get("sender_type"),      
                    "message": r.get("message"),              
                    "timestamp": r.get("timestamp"),      
                    "user_name": r.get("user_name"),       
                    "conversation_id": r.get("conversation_id")  
                })
        
        return history
        
    except Exception as e:
        dev_log(e, "ERR200")
        logging.error("Failed to retrieve conversation history for user %s", user_id[-4:])
        return []

def get_user_stats(user_id: str) -> dict:
    #get conversation statistics for a specific user. SECURITY: Only returns data for the specified user
    if collection is None:
        return {"error": "Database disabled"}
    
    try:
       
        user_filter = {"user_id": user_id}
        total_messages = collection.count_documents(user_filter)
        user_messages = collection.count_documents({**user_filter, "sender_type": "user"})
        bot_messages = collection.count_documents({**user_filter, "sender_type": "bot"})
        first_msg = collection.find_one(user_filter, sort=[("timestamp", 1)])
        last_msg = collection.find_one(user_filter, sort=[("timestamp", -1)])
        user_info = collection.find_one(
            {**user_filter, "user_name": {"$exists": True, "$ne": None}},
            sort=[("timestamp", -1)]
        )

        return {
            "user_id": user_id,
            "user_name": user_info.get("user_name") if user_info else "Unknown",
            "phone_number": user_info.get("phone_number") if user_info else user_id,
            "total_messages": total_messages,
            "user_messages": user_messages,
            "bot_messages": bot_messages,
            "first_message": first_msg.get("timestamp") if first_msg else None,
            "last_message": last_msg.get("timestamp") if last_msg else None,
            "conversation_id": f"chat_{user_id}"
        }
        
    except Exception as e:
        logging.error("Error getting user stats for %s: %s", user_id[-4:], e)
        return {"error": str(e)}

def get_all_users() -> list:
    #get a list of all users who have interacted with the bot
    if collection is None:
        return []
    
    try:
        user_ids = collection.distinct("user_id")
        users = []
        
        for user_id in user_ids:
            stats = get_user_stats(user_id)
            if "error" not in stats:
                users.append(stats)
        
        return sorted(users, key=lambda x: x.get("last_message", ""), reverse=True)
        
    except Exception as e:
        logging.error("Error getting all users: %s", e)
        return []

def is_first_time_user(user_id: str) -> bool:
  
    if collection is None:
        return True
    try:
        message_count = collection.count_documents({"user_id": user_id})
        return message_count == 0
    except Exception:
        return True

def build_welcome_message(user_name: str | None = None) -> str:
   #build welcome message for first-time users containing their name
    name = user_name or "there"
    return f"""👋 Hello {name}! Welcome to {BOT_NAME}!

By messaging me, you have agreed to our Terms of Service {TERMS_URL} and Privacy Policy {PRIVACY_URL}.

If you ever want help to  create your own WhatsApp bot or need help with the Meta API, you can contact the creator directly:
- WhatsApp: {CREATOR_WHATSAPP}
- Contact form: https://manases.space/contact-us
"""

def build_system_prompt(user_id: str = None) -> str:
    #build the system prompt that instructs the assistant about identity and user context
    try:
        #instruction.md contains the instructions given to the model we are interacting with so you can update the instructions there
        with open("prompts/instructions.md", "r", encoding="utf-8") as f:
            base_template = f.read()
    except Exception:
        base_template = "You are {BOT_NAME}, a helpful WhatsApp assistant created by {CREATOR_NAME}.\n"

    s = base_template.format(BOT_NAME=BOT_NAME, CREATOR_NAME=CREATOR_NAME)
    
    if user_id:
        #inject background dynamically fetched profile
        if db is not None:
            try:
                profile_doc = db["user_profiles"].find_one({"user_id": user_id})
                if profile_doc and profile_doc.get("profile_summary"):
                    s += f"\nUSER PROFILE & HISTORY:\n"
                    s += f"- {profile_doc.get('profile_summary')}\n"
            except Exception as e:
                logging.error("Failed to inject user profile into prompt: %s", e)

        location_data = get_user_location(user_id)
        s += f"\nUSER CONTEXT:\n"
        s += f"- Current user's phone number: {user_id}\n"
        if location_data:
            s += f"- User's location: {location_data['country_name']} (Code: {location_data['country_code']})\n"
            s += f"- Country dial code: {location_data['dial_code']}\n"
            s += f"- Provide responses relevant to {location_data['country_name']} culture and context\n"
        else:
            s += f"- Use the phone number country code to provide location-relevant information\n"
        s += f"- Tailor responses to be culturally and regionally appropriate\n"
    return s

def get_legal_links() -> dict:
    #gets the exact privacy policy and terms of service urls for the bot  use this whenever the user asks for legal links, terms, or privacy policies 
    return {"privacy_policy": PRIVACY_URL, "terms_of_service": TERMS_URL}

def get_creator_contact() -> dict:
    #gets the creator's direct contact information. Use this for support requests, data deletion requests, or when the user asks to build their own bot."""
    return {"whatsapp": CREATOR_WHATSAPP, "contact_form": "https://manases.space/contact-us", "email": CREATOR_EMAIL}

def generate_ai_reply_with_context(user_id: str, user_text: str = "", media_part=None) -> str:
    #fallback default
    default_reply = f"Echo: {user_text}" if user_text else "Media received."

    if not ai_client:
        return default_reply

    try:
        history = get_conversation_history(user_id, limit=MEMORY_LIMIT)
        system_prompt = build_system_prompt(user_id)   
        contents = []
        for h in history:
            role = "user" if h["sender_type"] == "user" else "model"
            if h.get("conversation_id") == f"chat_{user_id}":
                contents.append({"role": role, "parts": [{"text": h["message"]}]})
        
        user_parts = []
        if user_text:
            user_parts.append({"text": user_text})
        if media_part:
            user_parts.append(media_part)
            
        contents.append({"role": "user", "parts": user_parts})
        
        bot_tools = [get_legal_links, get_creator_contact]

        completion = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                tools=bot_tools
            )
        )
        
        if completion.function_calls:
            tool_responses = []
            for function_call in completion.function_calls:
                if function_call.name == "get_legal_links":
                    tool_responses.append(types.Part.from_function_response(name=function_call.name, response=get_legal_links()))
                elif function_call.name == "get_creator_contact":
                    tool_responses.append(types.Part.from_function_response(name=function_call.name, response=get_creator_contact()))
            
            #add the model's function call to history
            contents.append(completion.candidates[0].content)
            #add our responses
            contents.append({"role": "user", "parts": tool_responses})
            
            #generate the final response
            completion = ai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt
                )
            )

        ai_text = completion.text.strip()
        return ai_text or default_reply

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg.upper() or "QUOTA" in error_msg.upper() or "503" in error_msg or "SERVICE UNAVAILABLE" in error_msg.upper():
            logging.warning("Gemini 429/503 error detected. Switching to fallback Groq AI.")
            # Format history for fallback
            fallback_history = []
            for h in history:
                fallback_history.append({
                    "sender_type": h.get("sender_type"),
                    "conversation_id": h.get("conversation_id"),
                    "message": h.get("message", "")
                })
            return generate_fallback_reply_with_context(user_id, user_text or "Media received.", fallback_history, system_prompt)

        return make_user_safe_error("ERR400")

@app.route("/", methods=["GET"])
@app.route("/webhook", methods=["GET"])
def verify():
    #verification endpoint for WhatsApp webhoo
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == VERIFY_TOKEN:
        logging.info("200 Webhook validated")
        return challenge, 200
    logging.error("Invalid verification token")
    return "Invalid verification token", 403

@app.route("/", methods=["POST"])
@app.route("/webhook", methods=["POST"])
def webhook():
    #webhook entrypoint from WhatsApp
    data = request.get_json(silent=True) or {}
    logging.info("200 Received message")

    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages") or []
                contacts = value.get("contacts") or []
                
                if messages:
                    for message in messages:
                        user_id = message.get("from")
                        msg_type = message.get("type", "unknown")
                        user_name = None
                        user_phone = user_id
                        
                        #get user name from contacts
                        for contact in contacts:
                            if contact.get("wa_id") == user_id:
                                profile = contact.get("profile", {})
                                user_name = profile.get("name")
                                break
                        
                        if msg_type == "text":
                            text_body = (message.get("text") or {}).get("body")
                            if not text_body:
                                continue

                            is_new_user = is_first_time_user(user_id)
                            
                            #detect and update location stats for every interaction 
                            location_data = detect_user_location(user_id)
                            if location_data:
                                save_user_location(user_id, location_data, user_name)
                            
                            if is_new_user:
                                logging.info("New user registered")

                            #save user message to database 
                            saved = save_message_to_db(
                                user_id=user_id,
                                message=text_body,
                                sender_type="user",
                                message_type="text",
                                user_name=user_name,
                                phone_number=user_phone
                            )
                            if not saved:
                                send_message(user_id, make_user_safe_error("ERR100"))
                                continue

                            #send welcome message to new users
                            if is_new_user:
                                welcome_msg = build_welcome_message(user_name)
                                send_message(user_id, welcome_msg)
                                
                                save_message_to_db(
                                    user_id=user_id,
                                    message=welcome_msg,
                                    sender_type="bot",
                                    message_type="text",
                                    user_name=user_name,
                                    phone_number=user_phone
                                )
                                


                            #generate reply
                            reply_text = generate_ai_reply_with_context(user_id, text_body)

                            #send standard text reply to user
                            send_ok = send_message(user_id, reply_text)
                            if not send_ok:
                                logging.error("Failed to send WhatsApp message to %s", user_id)

                            #save bot reply to database
                            save_message_to_db(
                                user_id=user_id,
                                message=reply_text,
                                sender_type="bot",
                                message_type="text",
                                user_name=user_name,
                                phone_number=user_phone
                            )
                            
                            # trigger background profile update on every message as requested
                            if collection is not None:
                                threading.Thread(target=update_user_profile_in_background, args=(user_id, text_body, db, ai_client, user_name, location_data)).start()

                        elif msg_type == "image":
                            #handle images using Gemini
                            image_info = message.get("image", {})
                            media_id = image_info.get("id")
                            caption = image_info.get("caption", "Describe this image")
                            
                            #check rate limit for sending media
                            if not media.check_media_rate_limit(user_id, collection):
                                send_message(user_id, f"You have reached your daily limit for media processing ({media.MEDIA_LIMIT} per day). Please try again tomorrow.")
                                continue
                                
                            send_message(user_id, "Analyzing your image, please wait...")
                            
                            image_part = media.get_media_part(media_id)
                            if image_part:
                                processing_result = generate_ai_reply_with_context(
                                    user_id=user_id, 
                                    user_text=f"[User sent an image with caption: {caption}. Consider the image and respond in context.]", 
                                    media_part=image_part
                                )
                            else:
                                processing_result = "Sorry, I couldn't download the image."
                            
                            #save to message history
                            save_message_to_db(user_id, f"[IMAGE] {caption}", "user", "image")
                            save_message_to_db(user_id, processing_result, "bot", "text")
                            
                            send_message(user_id, processing_result)

                        elif msg_type == "audio":
                            audio_info = message.get("audio", {})
                            media_id = audio_info.get("id")
                            
                            if not media.check_media_rate_limit(user_id, collection):
                                send_message(user_id, f"You have reached your daily limit for media processing ({media.MEDIA_LIMIT} per day). Please try again tomorrow.")
                                continue
                            
                            send_message(user_id, "Listening to your voice note...")
                            
                            audio_part = media.get_media_part(media_id)
                            if audio_part:
                                processing_result = generate_ai_reply_with_context(
                                    user_id=user_id, 
                                    user_text="[User sent a voice note. Respond to what they said in the context of the conversation]", 
                                    media_part=audio_part
                                )
                            else:
                                processing_result = "Sorry, I couldn't download or listen to the audio."
                            
                            #save to message history
                            save_message_to_db(user_id, "[AUDIO MESSAGE]", "user", "audio")
                            save_message_to_db(user_id, processing_result, "bot", "text")
                            
                            send_message(user_id, processing_result)

                        elif msg_type == "document":
                            doc_info = message.get("document", {})
                            media_id = doc_info.get("id")
                            filename = doc_info.get("filename", "document")
                            
                            if not media.check_media_rate_limit(user_id, collection):
                                send_message(user_id, f"You have reached your daily limit for media processing ({media.MEDIA_LIMIT} per day). Please try again tomorrow.")
                                continue
                            
                            send_message(user_id, f"Reading {filename}...")
                            
                            doc_part = media.get_media_part(media_id)
                            if doc_part:
                                processing_result = generate_ai_reply_with_context(
                                    user_id=user_id, 
                                    user_text=f"[User sent a document named {filename}. Summarize or respond to its contents in the context of our chat.]", 
                                    media_part=doc_part
                                )
                            else:
                                processing_result = "Sorry, I couldn't download or analyze the document."
                            
                            #save to message history
                            save_message_to_db(user_id, f"[DOCUMENT: {filename}]", "user", "document")
                            save_message_to_db(user_id, processing_result, "bot", "text")
                            
                            send_message(user_id, processing_result)

                        else:
                            #handle other non-text messages
                            save_message_to_db(user_id, f"[{msg_type.upper()}]", "user", msg_type)
                            fallback = (f"I currently support text, image, audio, and document files! "
                                        f"I'll handle this {msg_type} as a placeholder.")
                            send_message(user_id, fallback)

                statuses = value.get("statuses") or []
                for status in statuses:
                    try:
                        msg_id = status.get("id")
                        recipient_id = status.get("recipient_id")
                        st = status.get("status")

                    except Exception:
                        logging.debug("Malformed status object: %s", status)

        return jsonify({"status": "received"}), 200

    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        dev_log(e, f"WEBHOOK_ERR_{error_id}")
        return jsonify({"status": "error", "error": f"Internal error {error_id}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logging.info("WhatsApp Bot starting on port %d", port)
    logging.info("Database: %s", "Connected" if collection is not None else "Disabled")
    logging.info("AI: %s", "Ready" if ai_client is not None else "Disabled") 
    logging.info("Location: %s", "Ready" if location_collection is not None else "Disabled")
    app.run(host="0.0.0.0", port=port, debug=False)
