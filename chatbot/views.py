from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
import json
import logging
from .chatbot import ChatBot

# Configure logging
logger = logging.getLogger(__name__)

# Initialize the chatbot as a singleton
try:
    chatbot = ChatBot()
    logger.info("ChatBot instance created successfully")
except Exception as e:
    logger.error(f"Failed to create ChatBot instance: {str(e)}")
    chatbot = None

@cache_page(60 * 15)  # Cache the chat page for 15 minutes
def chat_page(request):
    """Render the chat interface"""
    return render(request, 'chatBot/chat.html')

@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    if not chatbot:
        return JsonResponse({
            "success": False,
            "error": "ChatBot is not properly initialized. Please try again later."
        }, status=500)

    try:
        data = json.loads(request.body)
        user_input = data.get("message", "")

        if not user_input:
            return JsonResponse({
                "success": False,
                "error": "Please enter a message."
            })

        response = chatbot.get_response(user_input)
        return JsonResponse(response)

    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Invalid JSON format in request body."
        }, status=400)
    except Exception as e:
        logger.error(f"Error in chat_api: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": "An unexpected error occurred. Please try again."
        }, status=500)
