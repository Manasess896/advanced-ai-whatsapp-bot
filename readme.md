# 🤖 Intelligent WhatsApp Bot with AI & Location Detection

A WhatsApp bot powered by Groq API and open ai model, featuring intelligent conversations, persistent memory, location detection, and comprehensive user management.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-green?logo=flask)](https://flask.palletsprojects.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green?logo=mongodb)](https://mongodb.com/atlas)
[![Groq](https://img.shields.io/badge/AI-Groq%20LLaMA-orange)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

🔗 **Open Source:** Available on GitHub at [https://github.com/Manasess896/advanced-ai-whatsapp-bot](https://github.com/Manasess896/advanced-ai-whatsapp-bot)

---

## ✨ Key Features

### 🧠 **AI & Intelligence**

- **Advanced AI Models:** Powered by Groq's high-performance LLaMA models
- **Context-Aware Conversations:** Remembers conversation history for natural dialogue
- **Smart Memory Management:** Configurable message history limits for optimal performance
- **Fallback Handling:** Graceful error handling with user-friendly messages

### 🌍 **Location & Personalization**

- **Automatic Location Detection:** Identifies user's country from phone number
- **Location-Aware Responses:** Culturally appropriate and region-specific replies
- **Country Code Database:** Comprehensive database of 200+ country codes
- **Persistent User Profiles:** Stores user preferences and location data

### 🔒 **Privacy & Security**

- **GDPR Compliant:** Built-in privacy policy and data handling
- **User Data Isolation:** Strict per-user data access controls
- **Secure Error Handling:** No sensitive data leaked in error messages
- **Legal Framework:** Comprehensive Terms of Service included

### 📊 **Management & Monitoring**

- **Real-time Statistics:** Track messages, users, and engagement
- **User Management:** Individual user profiles and conversation stats
- **Admin Endpoints:** Built-in admin dashboard for monitoring
- **Comprehensive Logging:** Detailed logs with error tracking

### 🚀 **Developer Experience**

- **Easy Deployment:** One-click deployment to Heroku, Railway, or any cloud platform
- **Development Mode:** Auto-restart functionality for seamless development
- **Environment Configuration:** Secure environment variable management
- **Modular Design:** Clean, maintainable code structure

---

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed on your system
- **Git** for cloning the repository
- **MongoDB Atlas** account (free tier available)
- **Meta for Developers** account for WhatsApp Cloud API
- **Groq API** account for AI capabilities

### 📊 Free Tier Limits

- **MongoDB Atlas:** 512MB storage (sufficient for thousands of conversations)
- **Groq API:** Generous free tier with high-speed inference
- **WhatsApp Cloud API:** 1000 free messages per month
- **Heroku/Railway:** Free hosting with some limitations

## 🚀 Quick Start

### 1. **Clone & Install**

```bash
# Clone the repository
git clone https://github.com/Manasess896/Whatsapp-Bot.git
cd Whatsapp-Bot

# Install dependencies
python -m pip install -r requirements.txt
```

### 2. **Environment Configuration**

Create a `.env` file in the project root:

```env
# WhatsApp Cloud API Configuration
WHATSAPP_TOKEN=your_whatsapp_access_token
PHONE_NUMBER_ID=your_phone_number_id
VERIFY_TOKEN=your_webhook_verify_token

# AI Configuration
GROQ_API_KEY=your_groq_api_key

# Database Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database
DATABASE_NAME=whatsapp_bot
COLLECTION_NAME=conversations

# Bot Identity
BOT_NAME=Code Craft AI
CREATOR_NAME=Your Name
CREATOR_EMAIL=your.email@example.com
CREATOR_WHATSAPP=+1234567890

# URLs (update with your domain)
PRIVACY_URL=https://yourdomain.com/privacy
TERMS_URL=https://yourdomain.com/terms

# Performance Settings
MEMORY_LIMIT=30
DEBUG_LOGS=false
```

> 💡 **Security Tip:** Generate a secure verify token:
>
> ```python
> import secrets; print(secrets.token_hex(16))
> ```

### 3. **Service Setup**

#### 📱 **WhatsApp Cloud API Setup**

1. Visit [Meta for Developers](https://developers.facebook.com/apps)
2. Create a new app → Business → WhatsApp
3. Configure WhatsApp → Get access token and phone number ID
4. Add webhook URL: `https://your-domain.com/webhook`
5. Subscribe to `messages` webhook field

#### 🤖 **Groq AI Setup**

1. Sign up at [Groq Console](https://console.groq.com/keys)
2. Generate an API key
3. Add to your `.env` file

#### 🗄️ **MongoDB Atlas Setup**

1. Create account at [MongoDB Atlas](https://mongodb.com/atlas)
2. Create a free M0 cluster
3. Create database user with read/write access
4. Get connection string and add to `.env`
5. Whitelist your IP or allow access from anywhere (0.0.0.0/0)

### 4. **Local Development**

```bash
# Run with auto-restart (recommended for development)
python worker.py

# Or run directly
python main.py
```

### 5. **Expose to Internet (Development)**

```bash
# Install ngrok
# Visit: https://ngrok.com/download

# Start tunnel
ngrok http 5000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
# Add to Meta dashboard: https://abc123.ngrok.io/webhook
```

---


## 🔧 Development Features

### **Auto-Restart Development**

```bash
# Automatically restart on file changes
python worker.py
```


## 🧠 AI & Intelligence Features

### **Advanced AI Capabilities**

- **Model:** Groq's high-performance LLaMA models (`openai/gpt-oss-20B`)
- **Context Awareness:** Maintains conversation history for natural dialogue
- **Memory Management:** Configurable message limits (default: 30 messages)
- **Fallback Handling:** Graceful degradation when AI services are unavailable

### **Location Intelligence**

- **Automatic Detection:** Identifies user location from phone number
- **Cultural Awareness:** Provides region-appropriate responses
- **Country Database:** Supports 200+ countries with accurate detection
- **Persistent Storage:** Remembers user location for future conversations

### **Smart Features**

- **Welcome Messages:** Automatic onboarding for new users
- **Error Recovery:** User-friendly error messages with developer codes
- **Rate Limiting:** Built-in protection against spam
- **Data Validation:** Robust input validation and sanitization

---

## 📊 Database Structure & Collections

### **Conversations Collection**

```javascript
{
  "_id": ObjectId,
  "user_id": "254114471302",           // WhatsApp user ID (phone)
  "message": "Hello bot!",             // Message content
  "sender_type": "user",               // "user" or "bot"
  "message_type": "text",              // "text", "image", etc.
  "timestamp": ISODate,                // UTC timestamp
  "created_at": "2024-01-01T12:00:00Z", // ISO string format
  "user_name": "John Doe",             // User's WhatsApp name
  "phone_number": "+254114471302",     // Formatted phone
  "conversation_id": "chat_254114471302" // Conversation grouping
}
```

### **User Locations Collection**

```javascript
{
  "_id": ObjectId,
  "user_id": "254114471302",           // WhatsApp user ID
  "user_name": "John Doe",             // User's display name
  "country_name": "Kenya",             // Detected country
  "country_code": "KE",                // ISO country code
  "dial_code": "+254",                 // Country calling code
  "phone_number": "+254114471302",     // Original phone number
  "clean_phone": "254114471302",       // Digits only
  "mobile_number_length": 9,           // Expected length
  "first_detected": ISODate,           // First detection time
  "last_updated": ISODate,             // Last update time
  "detection_count": 3                 // Times detected
}
```

---

## 🛠️ API Endpoints

### **Webhook Endpoints**

- `GET /webhook` - WhatsApp webhook verification
- `POST /webhook` - Receive WhatsApp messages

### **Legal & Compliance**

- `GET /privacy` - Privacy policy page
- `GET /terms` - Terms of service page

### **Admin Functions** (Coming Soon)

- `GET /admin/stats` - Bot usage statistics
- `GET /admin/users` - User management panel

---

## 📚 Core Dependencies

| Library                                                      | Version | Purpose                               |
| ------------------------------------------------------------ | ------- | ------------------------------------- |
| **[Flask](https://flask.palletsprojects.com/)**              | 3.0+    | Web framework for webhook handling    |
| **[pymongo](https://pymongo.readthedocs.io/)**               | 4.6+    | MongoDB driver for data storage       |
| **[dnspython](https://dnspython.readthedocs.io/)**           | 2.4+    | DNS resolution for MongoDB Atlas      |
| **[groq](https://pypi.org/project/groq/)**                   | 0.8+    | Groq AI API client for LLaMA models   |
| **[python-dotenv](https://pypi.org/project/python-dotenv/)** | 1.0+    | Environment variable management       |
| **[requests](https://docs.python-requests.org/)**            | 2.32+   | HTTP requests to WhatsApp API         |
| **[gunicorn](https://gunicorn.org/)**                        | Latest  | WSGI server for production deployment |

---

## 🔑 Detailed Setup Guides

### 📱 **WhatsApp Cloud API Setup**

1. **Create Meta App:**

   - Go to [Meta for Developers](https://developers.facebook.com/apps)
   - Click "Create App" → Choose "Business" → "WhatsApp"
   - Fill in app details and create

2. **Configure WhatsApp:**

   - Navigate to WhatsApp → Getting Started
   - Copy the **Access Token** and **Phone Number ID**
   - Add to your `.env` file

3. **Set Webhook:**

   - In WhatsApp settings, add webhook URL: `https://your-domain.com/webhook`
   - Add your `VERIFY_TOKEN` from `.env`
   - Subscribe to `messages` field

4. **Test Integration:**
   - Send a test message from WhatsApp Business API Test Number
   - Check logs to confirm webhook is receiving messages

### 🤖 **Groq AI Configuration**

1. **Get API Key:**

   - Visit [Groq Console](https://console.groq.com/keys)
   - Sign up for free account
   - Generate API key

2. **Add to Environment:**

   ```env
   GROQ_API_KEY=gsk_your_api_key_here
   ```

### 🗄️ **MongoDB Atlas Configuration**

1. **Create Cluster:**

   - Sign up at [MongoDB Atlas](https://mongodb.com/atlas)
   - Create free M0 cluster (512MB)
   - Choose cloud provider and region

2. **Database Access:**

   - Create database user with read/write permissions
   - Note username and password

3. **Network Access:**

   - Add IP addresses or allow access from anywhere (0.0.0.0/0)
   - For production, restrict to your server IPs

4. **Connection String:**
   ```env
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database_name
   ```

---

## 🚀 Advanced Features & Customization

### **Location Intelligence**

The bot automatically detects user location from phone numbers:

```python
# Automatic country detection from phone number
location_data = detect_user_location("+254114471302")
# Returns: {'country_name': 'Kenya', 'country_code': 'KE', ...}
```

### **Message History Management**

```python
# Configurable memory limit
MEMORY_LIMIT = 30  # Number of messages to remember

# Conversation history with context
history = get_conversation_history(user_id, limit=MEMORY_LIMIT)
```

### **Error Handling System**

```python
# User-friendly error messages with developer codes
ERROR_MESSAGES = {
    "ERR100": "Database error - please try again",
    "ERR200": "Message history error",
    "ERR300": "Location detection error",
    "ERR400": "AI service unavailable"
}
```

### **Customization Options**

1. **Change AI Model:**

   ```python
   # In main.py, modify the model parameter
   completion = ai_client.chat.completions.create(
       model="openai/gpt-oss-20B",  # Change this
       messages=messages,
   )
   ```

2. **Custom System Prompts:**

   ```python
   def build_system_prompt(user_id: str = None) -> str:
       # Customize bot personality and instructions
       return f"You are {BOT_NAME}, a helpful assistant..."
   ```

3. **Add New Message Types:**
   ```python
   # Extend webhook to handle images, documents, etc.
   elif msg_type == "image":
       # Handle image messages
       pass
   ```

---



## 📊 Performance & Scaling

### **Optimization Tips**

- **Message Limits:** Keep `MEMORY_LIMIT` between 20-50 for optimal performance
- **Database Indexing:** MongoDB automatically indexes by `user_id` and `timestamp`
- **Caching:** Consider Redis for high-traffic deployments
- **Rate Limiting:** Implement request throttling for production

### **Monitoring & Analytics**

---

## 🙏 Acknowledgments

- **[Meta](https://developers.facebook.com/)** - WhatsApp Cloud API
- **[Groq](https://groq.com/)** - High-performance AI inference
- **[MongoDB](https://mongodb.com/)** - Flexible document database
- **[Flask](https://flask.palletsprojects.com/)** - Lightweight web framework
- **Open Source Community** - For inspiration and support

