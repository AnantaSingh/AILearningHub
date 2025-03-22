import os
import google.generativeai as genai
import dotenv
import logging
import re
from pathlib import Path
from django.conf import settings

# Configure logging
logger = logging.getLogger(__name__)

def get_api_key():
    # Try getting API key from environment first
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        # Try loading from .env file
        env_path = Path(__file__).parent.parent / '.env'
        if env_path.exists():
            dotenv.load_dotenv(env_path)
            api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        logger.error("GEMINI_API_KEY not found in environment variables or .env file")
        return None
    
    return api_key

def format_response(text):
    """Convert custom formatting to plain text with bold words and proper newlines."""
    # First, normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove any existing HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Convert text in parentheses to uppercase for bold effect
    text = re.sub(r'\(([^)]+)\)', lambda m: m.group(1).upper(), text)
    
    # Process text line by line
    paragraphs = text.split('\n\n')
    processed_paragraphs = []
    
    for paragraph in paragraphs:
        lines = paragraph.split('\n')
        processed_lines = []
        
        for line in lines:
            # Convert text in all caps to remain in uppercase
            def preserve_uppercase(match):
                return match.group(0).upper()
            
            line = re.sub(r'\b[A-Z][A-Z\s]+[A-Z]\b', preserve_uppercase, line)
            
            # Convert bold text markers to uppercase
            line = re.sub(r'••([^•]+?)••', lambda m: m.group(1).upper(), line)
            line = re.sub(r'\*\*([^*]+?)\*\*', lambda m: m.group(1).upper(), line)
            
            # Remove other formatting markers
            line = re.sub(r'\*([^*]+?)\*', r'\1', line)
            line = line.replace('••', '').replace('**', '')
            
            line = line.strip()
            if line:
                if line.startswith('•'):
                    # Handle main bullet points
                    if ':' in line:
                        title, desc = line.split(':', 1)
                        processed_lines.append(f"\n{title}:")
                        if desc.strip():
                            processed_lines.append(f"   {desc.strip()}")
                    else:
                        processed_lines.append(f"\n• {line[1:].strip()}")
                else:
                    processed_lines.append(line)
        
        if processed_lines:
            processed_text = '\n'.join(processed_lines)
            processed_paragraphs.append(processed_text)
    
    # Join paragraphs with double newlines
    text = '\n\n'.join(processed_paragraphs)
    
    # Clean up multiple spaces
    text = re.sub(r' +', ' ', text)
    
    # Ensure bullet points start on new lines
    text = re.sub(r'([^•])\n?• ', r'\1\n\n• ', text)
    
    # Clean up multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Add spacing after periods in sentences
    text = re.sub(r'\.(?=\S)', '. ', text)
    
    # Final cleanup
    text = text.strip()
    
    return text

def is_greeting(text):
    """Check if the input is a greeting."""
    # Clean and normalize the input text
    text = text.lower().strip()
    
    # Define strict greeting patterns
    greetings = [
        '^hello[!.?]?$',
        '^hi[!.?]?$',
        '^hey[!.?]?$',
        '^greetings[!.?]?$',
        '^good morning[!.?]?$',
        '^good afternoon[!.?]?$',
        '^good evening[!.?]?$'
    ]
    
    # Check if the text matches any greeting pattern exactly
    return any(re.match(pattern, text) for pattern in greetings)

# Get API key and configure Gemini
API_KEY = get_api_key()
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    logger.error("Failed to configure Gemini API - no API key available")

# List available models for debugging
try:
    for m in genai.list_models():
        logger.info(f"Available model: {m.name}")
except Exception as e:
    logger.error(f"Error listing models: {str(e)}")

class ChatBot:
    def __init__(self):
        self.api_key = get_api_key()
        if not self.api_key:
            logger.error("ChatBot initialization failed - no API key available")
            raise ValueError("GEMINI_API_KEY not found in environment variables or .env file")

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
            # Handle greetings
            if is_greeting(user_input):
                greeting_response = """Hello! 👋 I'm your AI Learning Assistant, specialized in artificial intelligence and machine learning. 
                
                I can help you with:
                - Understanding AI concepts
                - Learning about machine learning algorithms
                - Exploring deep learning architectures
                - Discussing latest AI trends and developments
                
                What would you like to learn about today?"""
                return {
                    "success": True,
                    "response": greeting_response
                }

            # System prompt to focus on AI topics
            system_prompt = """You are an AI Learning Assistant specialized in artificial intelligence, machine learning, deep learning, and related technologies. 

            Your responses should:
            1. Focus exclusively on AI/ML/DL topics
            2. Provide accurate, up-to-date information
            3. Include practical examples and use cases
            4. Explain concepts in a clear, structured way
            5. Use the following formatting:
               - Use ••text•• for key terms and concepts (no spaces between dots)
               - Use *text* for emphasis (no spaces between asterisks)
               - Start each bullet point with • (no asterisk)
               - Keep formatting consistent throughout the response
            6. If the question is not related to AI/ML/DL, politely redirect to AI topics

            Example format:
            ••Artificial Intelligence•• is a broad field of computer science. Here are its key components:

            • ••Machine Learning••: The ability to learn from data without explicit programming
            • ••Deep Learning••: A subset of ML using ••neural networks••
            • ••Natural Language Processing••: Understanding and generating human language

            Remember:
            - Always use proper formatting consistently
            - No spaces between dots in ••bold•• text
            - Use bullet points (•) for lists
            - Keep responses clear and well-structured

            If the user's question is not related to AI/ML/DL, respond with:
            "I'm specialized in AI and ML topics. Could you please rephrase your question to focus on artificial intelligence, machine learning, or related technologies?"
            """

            # Combine system prompt with user input
            prompt = f"{system_prompt}\n\nUser: {user_input}\n\nAssistant:"
            
            # Generate response with the focused prompt
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                # Format the response text
                formatted_response = format_response(response.text)
                return {
                    "success": True,
                    "response": formatted_response
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