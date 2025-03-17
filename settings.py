import os
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Google Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

INSTALLED_APPS = [
    # ... existing apps ...
    'accounts',
]

# Add these at the end of the file
LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'login' 