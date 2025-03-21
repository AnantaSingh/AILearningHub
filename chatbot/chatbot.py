import os
import google.generativeai as genai
import dotenv
import logging
from pathlib import Path
from django.conf import settings

# Configure logging
logger = logging.getLogger(__name__)

# Load API key from .env file
env_path = Path(__file__).parent.parent / '.env'
dotenv.load_dotenv(env_path)
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables")
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Configure Google Gemini API
genai.configure(api_key=API_KEY)

# List available models for debugging
try:
    for m in genai.list_models():
        logger.info(f"Available model: {m.name}")
except Exception as e:
    logger.error(f"Error listing models: {str(e)}")

class ChatBot:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.is_configured = False
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.is_configured = True

    def get_response(self, message):
        if not self.is_configured:
            return "Chatbot is not configured. Please set GEMINI_API_KEY in environment variables."
        try:
            response = self.model.generate_content(message)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"