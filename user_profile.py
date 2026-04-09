import logging
import time
from google.genai import types

logger = logging.getLogger(__name__)

def update_user_profile_in_background(user_id: str, new_message: str, db, ai_client):
    if db is None or ai_client is None:
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
            "Write a single, concise paragraph (max 50 words) summarizing their persona, name, interests, and ongoing topics. "
            "Incorporate new facts from the recent messages into the existing summary. "
            "Do not use bullet points or JSON. Only output the paragraph."
        )

        prompt = f"Current Profile Summary:\n{current_profile_text}\n\nNew Message from User:\n{new_message}"

        #using gemini-1.5-flash for background tasks if you want separate quotas, but sticking to your default use gemini-2.5-flash or whatever you prefer
        response = ai_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3
            )
        )

        new_profile_summary = response.text.strip()

        #save generated summary to DB
        profile_collection.update_one(
            {"user_id": user_id},
            {"$set": {"profile_summary": new_profile_summary, "last_updated": new_profile_summary}},
            upsert=True
        )

    except Exception as e:
        logger.error("Error updating user profile in background: %s", e)
