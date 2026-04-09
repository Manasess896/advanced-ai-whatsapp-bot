# Intelligent WhatsApp Bot with AI and Location Detection

A WhatsApp bot powered by the Gemini API and its AI models, featuring intelligent conversations, persistent memory, location detection, and comprehensive user management.
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-green?logo=flask)](https://flask.palletsprojects.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green?logo=mongodb)](https://mongodb.com/atlas)
[![Groq](https://img.shields.io/badge/AI-Groq%20LLaMA-orange)](https://groq.com)
[![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-8E75B2?logo=googlegemini)](https://gemini.google.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
**Open Source:** Available on GitHub at [https://github.com/Manasess896/advanced-ai-whatsapp-bot](https://github.com/Manasess896/advanced-ai-whatsapp-bot)

*(Looking for the simpler, memoryless initial version? Check out the [Original Whatsapp-Bot repository](https://github.com/Manasess896/Whatsapp-Bot) featuring Groq/LLaMA without database state dependencies.)*

## Overview

This project provides an advanced WhatsApp bot capable of maintaining context-aware conversations, primarily utilizing the Gemini API for robust AI processing, with Groq functioning as a reliable fallback when needed. It includes robust location detection based on phone numbers, persistent user profiling via MongoDB, and secure data handling practices.

## Key Improvements

- **Enhanced AI Context:** Improved memory management for more natural, extended conversations.
- **Robust Location Intelligence:** Upgraded detection logic for more accurate cultural and regional responses.
- **Optimized Performance:** Better handling of fallback scenarios and rate limiting to ensure continuous availability.
- **Strict Data Privacy:** GDPR-compliant data isolation and error handling systems.

## Key Features

- **Advanced AI :** Powered by Google's Gemini models for primary inference, backed by Groq's high-performance LLaMA models for robust fallback and fast, dedicated background user profiling.
- **Context-aware conversations:** Remembers conversation history for natural dialogue.
- **Smart memory management:** Configurable message history limits for optimal performance.
- **Location detection:** Automatically identifies the user's country from their phone number to provide location-aware responses.
- **Persistent user profiles:** Stores user preferences and location data securely.
- **Privacy and security:** Built-in privacy policy, strict per-user data access controls, and secure error handling.

## Prerequisites

Before beginning the installation, ensure you have the following:

- Python 3.8 or higher installed on your system.
- Git for cloning the repository.
- A MongoDB Atlas account (the free tier is sufficient).
- A Meta for Developers account for accessing the WhatsApp Cloud API.
- A Google Gemini API key for primary AI capabilities.
- A Groq API account for fallback AI inference.

## Quick Start

### 1. Clone and Install

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/Manasess896/advanced-ai-whatsapp-bot.git
cd advanced-ai-whatsapp-bot
python -m pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the root directory of the project and populate it with the following configuration:

```env
# WhatsApp cloud API configuration
WHATSAPP_TOKEN=your_whatsapp_access_token
PHONE_NUMBER_ID=your_phone_number_id
VERIFY_TOKEN=your_webhook_verify_token

# AI configuration
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key

# Database configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database
DATABASE_NAME=whatsapp_bot
COLLECTION_NAME=conversations

# Bot Identity
BOT_NAME=Code Craft AI
CREATOR_NAME=Your Name
CREATOR_EMAIL=your.email@example.com
CREATOR_WHATSAPP=+1234567890

# URLs (Update with your domain)
PRIVACY_URL=https://yourdomain.com/privacy
TERMS_URL=https://yourdomain.com/terms

# Performance settings
MEMORY_LIMIT=5
DEBUG_LOGS=false
```

### 3. Service Setup

#### WhatsApp Cloud API Setup
1. **Create Meta App:**
   - Go to [Meta for Developers](https://developers.facebook.com/)
   - Click "Create App" → Choose "Business" → "WhatsApp"
   - Fill in app details and create
2. **Configure WhatsApp:**
   - Navigate to WhatsApp → Getting Started
   - Copy the Access Token and Phone Number ID
   - Add to your `.env` file
3. **Set Webhook:**
   - In WhatsApp settings, add webhook URL: `https://your-domain.com/webhook` (or use your ngrok URL for local testing)
   - Add your VERIFY_TOKEN from `.env`
   - Subscribe to messages field
4. **Test Integration:**
   - Send a test message from WhatsApp Business API Test Number
   - Check logs to confirm webhook is receiving messages

#### AI Configuration Setup
**Gemini API Configuration (Primary)**
1. **Get API Key:**
   - Obtain an API key from Google AI Studio.
2. **Add to Environment:**
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

**Groq AI Configuration (Fallback & Profiling)**
1. **Get API Key:**
   - Visit Groq Console
   - Sign up for free account
   - Generate API key
2. **Add to Environment:**
   ```env
   GROQ_API_KEY=gsk_your_api_key_here
   ```

#### MongoDB Atlas Configuration
1. **Create Cluster:**
   - Sign up at MongoDB Atlas
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

### 4. Local Development

Run the application using the worker script for auto-restarting during development, or run the main script directly:

```bash
# Run with auto-restart (recommended for development)
python worker.py

# Or run directly
python main.py
```

### 5. Exposing Local Server (Development)

To expose your local server to the internet for webhook testing, you can use ngrok:

1. **Install ngrok:**
   - Sign up and download ngrok from [https://ngrok.com/download](https://ngrok.com/download).
   - Authenticate your ngrok installation with your auth token.

2. **Start the tunnel:**
   ```bash
   ngrok http 5000
   ```

3. **Configure the Webhook in Meta for Developers:**
   - Copy the generated HTTPS Forwarding URL (e.g., `https://abc123.ngrok-free.app`).
   - Go to your app dashboard on [Meta for Developers](https://developers.facebook.com/).
   - Under **WhatsApp > Configuration**, click **Edit** for the webhook.
   - Set the Callback URL to your ngrok URL appended with `/webhook` (e.g., `https://abc123.ngrok-free.app/webhook`).
   - Enter the `VERIFY_TOKEN` you set in your `.env` file.
   - Save and ensure you've subscribed to the `messages` event.

## Architecture and Database Structure

### Data Collections

**Conversations**
Stores message history for context-awareness. Includes message content, timestamps, sender types, and conversation grouping IDs.

**User Locations**
Stores detected geographic data based on phone numbers. Includes country codes, dial codes, and detection timestamps to allow for localized responses.

## Core Dependencies

- Flask: Web framework for handling webhooks.
- PyMongo: MongoDB driver for data storage.
- DNSPython: DNS resolution for MongoDB Atlas connections.
- Google Generative AI (google-generativeai): API client for primary AI inference.
- Groq: API client for fallback AI inference.
- Python-dotenv: Environment variable management.
- Requests: HTTP client for interacting with the WhatsApp API.
- Gunicorn: WSGI server for production deployments.

## License

This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute this project under the terms of the license.
