import os
import logging
from groq import Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
fallback_client = None
if GROQ_API_KEY:
    try:
        fallback_client = Groq(api_key=GROQ_API_KEY)
        logging.info("200 Fallback AI service ready (Groq)")
    except Exception as e:
        logging.error("Fallback AI service failed: %s", e)
else:
    logging.warning("No Groq API key configured for fallback")

def generate_fallback_reply_with_context(user_id: str, user_text: str, history: list, system_prompt: str) -> str:
    #Fallback method using Groq API when Gemini fails with 429
    default_reply = f"Echo: {user_text}" if user_text else "Media received."

    if not fallback_client:
        return default_reply

    try:
        messages = [{"role": "system", "content": system_prompt}]
        
        for h in history:
            role = "user" if h["sender_type"] == "user" else "assistant"
            if h.get("conversation_id") == f"chat_{user_id}":
                messages.append({"role": role, "content": h["message"]})
                
        messages.append({"role": "user", "content": user_text})

        completion = fallback_client.chat.completions.create(
            model="openai/gpt-oss-20B",  #retaining the model from version 1
            messages=messages,
        )
        ai_text = completion.choices[0].message.content.strip()
        return ai_text or default_reply

    except Exception as e:
        logging.error("Fallback Groq Error: %s", e)
        return "I encountered a problem processing your request even with my fallback system. Please try again later."
