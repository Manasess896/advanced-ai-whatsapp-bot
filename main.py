# WhatsApp Bot with memory and meta api integration
import os
import requests
import logging
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from groq import Groq
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from datetime import datetime, timezone
import traceback
import uuid

load_dotenv(override=True)  # Force reload env variables

app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MONGO_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")#import collection for storing the conversations this is set in .env file 
LOCATION_COLLECTION_NAME = "user_locations"  # a collection for storing location data

BOT_NAME = os.getenv("BOT_NAME")
CREATOR_NAME = os.getenv("CREATOR_NAME")
CREATOR_EMAIL = os.getenv("CREATOR_EMAIL")  
CREATOR_WHATSAPP = os.getenv("CREATOR_WHATSAPP")
PRIVACY_URL = os.getenv("PRIVACY_URL")
TERMS_URL = os.getenv("TERMS_URL")
MEMORY_LIMIT = int(os.getenv("MEMORY_LIMIT", "30"))  # messages (user+bot) to keep for prompt


ERROR_MESSAGES = {
    "ERR100": "I encountered a problem when processing your request. Please tell the developer: ERR100.",
    "ERR200": "I encountered a problem when processing your request. Please tell the developer: ERR200.",
    "ERR300": "I encountered a problem when processing your request. Please tell the developer: ERR300.",
    "ERR400": "AI service is unavailable. Please try again later. (ERR400)"
}

def dev_log(exc: Exception, code: str):
  
    logging.error("Developer error %s: %s", code, exc)
    logging.error(traceback.format_exc())


ai_client = None
if GROQ_API_KEY:
    try:
        ai_client = Groq(api_key=GROQ_API_KEY)
        logging.info("200 AI service ready")
    except Exception as e:
        dev_log(e, "ERR400")
        ai_client = None
        logging.error("AI service failed")
else:
    logging.error("No AI API key configured")

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
        
        # testing  the connection
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
    """Return a short message for the user while logging details to dev logs."""
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
            # Update existing location
            location_collection.update_one(
                {"user_id": user_id},
                {"$set": location_doc}
            )
        else:
            # Insert new location
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
    """Send a text message via WhatsApp Cloud API. Returns True on success."""
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
   # Build welcome message for first-time users
    name = user_name or "there"
    return f"""👋 Hello {name}! Welcome to {BOT_NAME}!

By messaging me, you have agreed to our Terms of Service {TERMS_URL} and Privacy Policy {PRIVACY_URL}.
"""

def build_system_prompt(user_id: str = None) -> str:
    #build the system prompt that instructs the assistant about identity and user context
    s = f"You are {BOT_NAME}, a helpful WhatsApp assistant created by {CREATOR_NAME}.\n\n"
    if user_id:
        location_data = get_user_location(user_id)
        s += f"USER CONTEXT:\n"
        s += f"- Current user's phone number: {user_id}\n"
        if location_data:
            s += f"- User's location: {location_data['country_name']} (Code: {location_data['country_code']})\n"
            s += f"- Country dial code: {location_data['dial_code']}\n"
            s += f"- Provide responses relevant to {location_data['country_name']} culture and context\n"
        else:
            s += f"- Use the phone number country code to provide location-relevant information\n"
        s += f"- Tailor responses to be culturally and regionally appropriate\n\n"
    s += "BOT BEHAVIOR:\n"
    s += "- Keep replies concise (1-3 sentences) suitable for WhatsApp\n"
    s += "- Use conversation history for context when relevant\n"
    s += "- Be helpful, friendly, and informative\n"
    s += "- Provide location-aware responses based on user's country code\n"
    s += "- Don't invent facts about users or make assumptions beyond their phone number location\n\n"
    
    s += "PRIVACY & SECURITY RULES:\n"
    s += "- NEVER share information about other users or conversations\n"
    s += "- ONLY discuss data related to the current user\n"
    s += "- Don't reveal sensitive technical details \n"
    s += "- Dont talk about the bot database or sensitive matters concerning the bot \n\n"
    
    s += "LEGAL INFORMATION & LINKS:\n"
    s += f"- Privacy Policy URL: {PRIVACY_URL}\n"
    s += f"- Terms of Service URL: {TERMS_URL}\n"
    s += "- IMPORTANT: Always use these EXACT URLs when users ask about privacy or terms\n"
    s += "- Do NOT create or suggest alternative links - only use the URLs provided above\n"
    s += "- When asked about privacy policy, respond with the Privacy Policy URL\n"
    s += "- When asked about terms of service, respond with the Terms of Service URL\n"
    s += "- Users automatically agree to terms by messaging the bot\n"
    s += f"- For support or data deletion requests, direct users to contact: {CREATOR_EMAIL}\n\n"
    
    s += "GUIDELINES:\n"
    s += "- Don't repeat old messages verbatim from history\n"
    s += "- For technical questions, keep answers general and user-focused\n"
    s += "- Direct data deletion requests to contact the developer via appropriate channels\n"
    s += f"- CRITICAL: When users ask about privacy policy, ALWAYS respond with: {PRIVACY_URL}\n"
    s += f"- CRITICAL: When users ask about terms of service, ALWAYS respond with: {TERMS_URL}\n"
    s += "- Never create fake GitHub links or alternative URLs for legal documents\n"
    return s

def generate_ai_reply_with_context(user_id: str, user_text: str) -> str:
    # fallback default
    default_reply = f"Echo: {user_text}"

    if not ai_client:
        return default_reply

    try:
        history = get_conversation_history(user_id, limit=MEMORY_LIMIT)
        system_prompt = build_system_prompt(user_id)
        messages = [{"role": "system", "content": system_prompt}]
        for h in history:
            role = "user" if h["sender_type"] == "user" else "assistant"
            if h.get("conversation_id") == f"chat_{user_id}":
                messages.append({"role": role, "content": h["message"]})
        messages.append({"role": "user", "content": user_text})

        completion = ai_client.chat.completions.create(
            model="openai/gpt-oss-20B",
            messages=messages,
        )
        ai_text = completion.choices[0].message.content.strip()  # type: ignore
        return ai_text or default_reply

    except Exception as e:
        dev_log(e, "ERR400")
        return make_user_safe_error("ERR400")

@app.route("/webhook", methods=["GET"])
def verify():
    #Verification endpoint for WhatsApp webhoo
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == VERIFY_TOKEN:
        logging.info("200 Webhook validated")
        return challenge, 200
    logging.error("Invalid verification token")
    return "Invalid verification token", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    """Main webhook entrypoint from WhatsApp."""
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
                            
                            #nly detect location for new users (phone numbers don't change countries)
                            if is_new_user:
                                location_data = detect_user_location(user_id)
                                if location_data:
                                    save_user_location(user_id, location_data, user_name)
                            
                            if is_new_user:
                                logging.info("New user registered")

                            # save user message to database
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

                            # send welcome message to new users
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
                                


                            # generate AI reply
                            reply_text = generate_ai_reply_with_context(user_id, text_body)

                            # save bot reply to database
                            save_message_to_db(
                                user_id=user_id,
                                message=reply_text,
                                sender_type="bot",
                                message_type="text",
                                user_name=user_name,
                                phone_number=user_phone
                            )

                            # send reply to user
                            send_ok = send_message(user_id, reply_text)
                            if not send_ok:
                                logging.error("Failed to send WhatsApp message to %s", user_id)

                        else:
                            # handle non-text messages
                            save_message_to_db(user_id, f"[{msg_type.upper()}]", "user", msg_type)
                            fallback = ("I currently support text messages only. "
                                        "Please send your request as text.")
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
