# 🤖 Intelligent WhatsApp Bot with AI & Location Detection

A production-ready WhatsApp bot powered by Groq AI, featuring intelligent conversations, persistent memory, location detection, and comprehensive user management. Built with Flask and designed for easy deployment to cloud platforms.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-green?logo=flask)](https://flask.palletsprojects.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green?logo=mongodb)](https://mongodb.com/atlas)
[![Groq](https://img.shields.io/badge/AI-Groq%20LLaMA-orange)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

🔗 **Open Source:** Available on GitHub at [https://github.com/Manasess896/Whatsapp-Bot](https://github.com/Manasess896/Whatsapp-Bot)

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

## 🚀 Production Deployment

### **Heroku Deployment** (Recommended)

```bash
# Install Heroku CLI
# Visit: https://devcenter.heroku.com/articles/heroku-cli

# Login and create app
heroku login
heroku create your-bot-name

# Set environment variables
heroku config:set WHATSAPP_TOKEN=your_token
heroku config:set PHONE_NUMBER_ID=your_phone_id
heroku config:set VERIFY_TOKEN=your_verify_token
heroku config:set GROQ_API_KEY=your_groq_key
heroku config:set MONGODB_URI=your_mongodb_uri
heroku config:set DATABASE_NAME=whatsapp_bot
heroku config:set COLLECTION_NAME=conversations
# ... add all other variables

# Deploy
git push heroku main

# Set webhook URL in Meta dashboard to:
# https://your-bot-name.herokuapp.com/webhook
```

### **Railway Deployment**

1. Connect your GitHub repository to [Railway](https://railway.app)
2. Add all environment variables in Railway dashboard
3. Deploy automatically on git push

### **Other Platforms**

- **Render:** Simple deployment with free tier
- **DigitalOcean App Platform:** Production-ready hosting
- **AWS Elastic Beanstalk:** Enterprise-scale deployment

---

## 🔧 Development Features

### **Auto-Restart Development**

```bash
# Automatically restart on file changes
python worker.py
```

### **Environment Management**

- Secure `.env` file handling
- Environment-specific configurations
- Debug mode toggle

### **Logging & Monitoring**

- Structured logging with timestamps
- Error tracking with unique IDs
- Performance monitoring

---

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

3. **Test AI Connection:**
   ```python
   from groq import Groq
   client = Groq(api_key="your_api_key")
   # Bot will automatically test connection on startup
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

## 🔒 Privacy & Legal Framework

### **Built-in Legal Compliance**

- ✅ **GDPR Compliant:** Transparent data collection and processing
- ✅ **Privacy Policy:** Comprehensive data handling disclosure
- ✅ **Terms of Service:** User agreement and liability protection
- ✅ **Data Rights:** User data access and deletion procedures
- ✅ **Consent Management:** Automatic terms acceptance workflow

### **Privacy Features**

- **Data Isolation:** Per-user data access controls
- **Secure Storage:** Encrypted data transmission and storage
- **Minimal Collection:** Only necessary data is stored
- **Retention Limits:** Configurable message history limits
- **Audit Logging:** Comprehensive activity logging

### **User Rights**

- **Access:** Users can request their data
- **Deletion:** Contact developer for data removal
- **Portability:** Data export capabilities
- **Correction:** Update personal information

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

## 🔧 Troubleshooting Guide

### **Common Issues & Solutions**

| Issue                  | Cause                  | Solution                               |
| ---------------------- | ---------------------- | -------------------------------------- |
| Bot not responding     | Missing `GROQ_API_KEY` | Add valid Groq API key to `.env`       |
| Database errors        | MongoDB connection     | Check `MONGODB_URI` and network access |
| Webhook failures       | Wrong URL/token        | Verify webhook URL and `VERIFY_TOKEN`  |
| Location detection off | Country codes missing  | Ensure `codes.json` file exists        |
| Memory issues          | High `MEMORY_LIMIT`    | Reduce limit or optimize queries       |

### **Debug Mode**

```env
DEBUG_LOGS=true  # Enable detailed logging
```

### **Health Check Commands**

```bash
# Test MongoDB connection
python -c "from pymongo import MongoClient; print('Connected!' if MongoClient('your_uri').admin.command('ping') else 'Failed')"

# Test Groq API
python -c "from groq import Groq; print('AI Ready!' if Groq(api_key='your_key') else 'Failed')"

# Test WhatsApp API
curl -X GET "https://graph.facebook.com/v21.0/me?access_token=YOUR_TOKEN"
```

---

## 📊 Performance & Scaling

### **Optimization Tips**

- **Message Limits:** Keep `MEMORY_LIMIT` between 20-50 for optimal performance
- **Database Indexing:** MongoDB automatically indexes by `user_id` and `timestamp`
- **Caching:** Consider Redis for high-traffic deployments
- **Rate Limiting:** Implement request throttling for production

### **Monitoring & Analytics**

```python
# Built-in user statistics
stats = get_user_stats(user_id)
# Returns: message counts, first/last message times, user info

# All users overview
all_users = get_all_users()
# Returns: sorted list of all users with statistics
```

### **Production Considerations**

- Use environment-specific configurations
- Implement proper logging and monitoring
- Set up automated backups for MongoDB
- Use process managers (PM2, systemd) for reliability
- Implement health checks and restart policies

---

## 🤝 Contributing

We welcome contributions! Here's how to get involved:

### **Setup Development Environment**

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/Whatsapp-Bot.git
cd Whatsapp-Bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Fill in your API keys and configuration
```

### **Development Guidelines**

- Follow PEP 8 style guidelines
- Add comprehensive docstrings
- Write tests for new features
- Update documentation for changes
- Use meaningful commit messages

### **Pull Request Process**

1. Create a feature branch: `git checkout -b feature-name`
2. Make your changes and test thoroughly
3. Update documentation if needed
4. Submit a pull request with detailed description

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support & Community

- **GitHub Issues:** [Report bugs](https://github.com/Manasess896/Whatsapp-Bot/issues)
- **Discussions:** [Feature requests & help](https://github.com/Manasess896/Whatsapp-Bot/discussions)
- **Email:** manasesskamau1053@gmail.com
- **WhatsApp:** +254114471302

---

## 🙏 Acknowledgments

- **[Meta](https://developers.facebook.com/)** - WhatsApp Cloud API
- **[Groq](https://groq.com/)** - High-performance AI inference
- **[MongoDB](https://mongodb.com/)** - Flexible document database
- **[Flask](https://flask.palletsprojects.com/)** - Lightweight web framework
- **Open Source Community** - For inspiration and support

---

<div align="center">

**⭐ Star this repo if you found it helpful!**

**[🚀 Deploy Now](https://heroku.com/deploy)** | **[📖 Documentation](https://github.com/Manasess896/Whatsapp-Bot/wiki)** | **[💬 Support](https://github.com/Manasess896/Whatsapp-Bot/discussions)**

_Built with ❤️ by developers, for developers_

</div>

1. Go to [Meta Business Dashboard](https://business.facebook.com/)
2. Open **Meta Business Settings**
3. Ensure you're in the correct Business Account with your WhatsApp number

### Step 2: Check User Roles

1. Navigate to **Accounts → WhatsApp Accounts**
2. Select your WhatsApp account
3. Ensure your system user has **Admin** access

⚠️ **Important:** Without proper roles, you won't be able to generate a valid token.

### Step 3: Create System User

1. Go to **Users → System Users**
2. Add new system user (e.g., `whatsapp-bot-user`)
3. Assign **Admin** role

### Step 4: Configure Permissions

1. In **System User → Assign Assets**, attach your WhatsApp account
2. Grant required permissions:
   - `whatsapp_business_messaging`
   - `whatsapp_business_management`
3. Save changes

### Step 5: Generate Token

1. In System User section, click **Generate Token**
2. Select your WhatsApp App
3. Choose required permissions
4. Select **Never Expire** (if available)
5. Copy token to your `.env` file

## 🚀 Deployment

For production deployment:

1. **Use environment variables** for all sensitive data
2. **Enable HTTPS** with proper SSL certificates
3. **Set up monitoring** using the admin endpoints
4. **Configure MongoDB Atlas** with proper security settings
5. **Use system user tokens** for reliability

## 🤝 Contributing

This is an open-source project! Contributions are welcome:

1. Fork the repository on [GitHub](https://github.com/Manasess896/Whatsapp-Bot)
2. Create a feature branch
3. Make your improvements
4. Submit a pull request

## 📞 Support

- **Issues:** Report bugs on [GitHub Issues](https://github.com/Manasess896/Whatsapp-Bot/issues)
- **Data Deletion:** Contact developer email (set in `DEVELOPER_EMAIL`)
- **Documentation:** This README and inline code comments
