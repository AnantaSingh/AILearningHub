import os
import google.generativeai as genai
import dotenv
import logging
from pathlib import Path

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
        try:
            # Initialize the model with the latest Gemini Pro model
            self.model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
            logger.info("ChatBot initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ChatBot: {str(e)}")
            raise

    def get_response(self, user_input):
        """Generate a response using Google's Gemini API."""
        if not user_input.strip():
            return {"success": False, "error": "Please ask something specific about AI or ML."}

        try:
            # System prompt to focus on AI topics
            system_prompt = """You are an AI Learning Assistant specialized in artificial intelligence, machine learning, deep learning, and related technologies. 
            Your responses should:
            1. Focus exclusively on AI/ML/DL topics
            2. Provide accurate, up-to-date information
            3. Include practical examples and use cases
            4. Explain concepts in a clear, structured way
            5. Use markdown formatting for better readability
            6. If the question is not related to AI/ML/DL, politely redirect to AI topics
            
            If the user's question is not related to AI/ML/DL, respond with:
            "I'm specialized in AI and ML topics. Could you please rephrase your question to focus on artificial intelligence, machine learning, or related technologies?"
            """

            # Combine system prompt with user input
            prompt = f"{system_prompt}\n\nUser: {user_input}\n\nAssistant:"
            
            # Generate response with the focused prompt
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return {
                    "success": True,
                    "response": response.text
                }
            else:
                return {
                    "success": False,
                    "error": "I couldn't generate a response. Can you rephrase?"
                }
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error details: {e.__dict__}")
            return {
                "success": False,
                "error": f"An error occurred: {str(e)}"
            }