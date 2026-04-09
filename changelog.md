# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - Current Release

### Added
- **Primary AI engine**: Integrated the Google Gemini API (`google-generativeai`) as the primary inference engine for advanced reasoning and improved conversation handling.
- **Resilient fallback mechanism**: Introduced a reliable fallback system (`fallback.py`) that routes requests to the Groq API (LLaMA models) if the Gemini API is unresponsive or encounters limits.
- **codebase Architecture**: Refactored the  version 1 script into a modular architecture featuring specialized files (`fallback.py`, `media.py`, `user_profile.py`, `worker.py`) for better scalability and maintainability.

### Changed
- **Dependencies**: Updated `requirements.txt` to include the Google Generative AI SDK alongside existing dependencies.
- **Configuration**: `GEMINI_API_KEY` was added as a core requirement to the `.env` configuration file.
- **Documentation**: Thoroughly overhauled the `readme.md` to reflect new services, improved setup configuration steps (including local ngrok setup and webhook configurations), and removed informal formatting.

### Improved
- **Enhanced Location Intelligence**: Upgraded the detection logic mapped to phone numbers for more accurate regional and cultural AI contextualization.
- **Performance & Error Handling**: Implemented better rate-limiting handling, secure data isolation mechanisms, and graceful failure degradation to maintain bot availability.

---

## [1.0.0] - Version 1 (Persistent Memory Update)

### Added
- **WhatsApp Integration**: Core webhook implementation allowing connections to the WhatsApp Cloud API.
- **Groq AI Implementation**: Initial conversational capabilities utilizing Groq's LLaMA models for all generations.
- **Context-Aware Memory**: Integrated MongoDB Atlas to persist conversation histories up to a predefined limit.
- **Basic User Profiling**: Implemented basic phone-number-based country detections and user profile tracking inside `main.py`.

---

## [0.1.0] - Memoryless Agent (Initial Release)

A simple, initial version of the WhatsApp bot focused on straightforward question-and-answer functionality. See the source repository here: [Whatsapp-Bot](https://github.com/Manasess896/Whatsapp-Bot).

### Added
- Built with Flask to receive WhatsApp messages via Meta's webhook.
- Replies using Groq's LLaMA models (`llama3-8b-8192` by default).
- Handles incoming messages and status updates (delivered/read).
- Deployed on Python 3.8+.
- `.env`-based configuration (WhatsApp Cloud API access and Groq API key).
