import logging
import time
import os
from groq import Groq

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = None
if GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        logger.error(f"Groq setup failed for user profile: {e}")

def update_user_profile_in_background(user_id: str, new_message: str, db, ai_client=None, user_name: str | None = None, location_data: dict | None = None):
    if db is None or groq_client is None:
        return

    #add a slight delay so it doesn't fire at the exact same millisecond as the main chat response
    time.sleep(5)

    try:
        profile_collection = db["user_profiles"]
        
        #fetch existing profile
        existing_profile = profile_collection.find_one({"user_id": user_id})
        current_profile_text = "No existing profile."
        if existing_profile and existing_profile.get("profile_summary"):
            current_profile_text = existing_profile.get("profile_summary")

        system_instruction = (
            "You are a user profiler. Read the user's current summary and recent message. "
            "Write a single, concise paragraph (max 50 words) summarizing their persona, name, interests, ongoing topics, and cultural context based on their location. "
            "Incorporate new facts from the recent messages into the existing summary. "
            "Do not use bullet points or JSON. Only output the paragraph."
        )

        country = location_data.get('country_name', 'Unknown') if location_data else 'Unknown'
        prompt = f"Current Profile Summary:\n{current_profile_text}\n\nUser Name: {user_name or 'Unknown'}\nLocation (Country): {country}\n\nNew Message from User:\n{new_message}"

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]

        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3
        )

        new_profile_summary = completion.choices[0].message.content.strip()

        #save generated summary to DB
        profile_collection.update_one(
            {"user_id": user_id},
            {"$set": {"profile_summary": new_profile_summary, "last_updated": new_profile_summary}},
            upsert=True
        )

    except Exception as e:
        logger.error("Error updating user profile in background: %s", e)
