from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.cache import cache_page
import json
from .chatbot import ChatBot

# Initialize the chatbot as a singleton
chatbot = ChatBot()

@cache_page(60 * 15)  # Cache the chat page for 15 minutes
def chat_page(request):
    """Render the chat interface"""
    return render(request, 'chatBot/chat.html')

@require_POST
def chat_api(request):
    """Handle chat API requests"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        
        if not message:
            return JsonResponse({
                'success': False,
                'error': 'Message is required'
            }, status=400)
        
        response = chatbot.get_response(message)
        
        return JsonResponse({
            'success': True,
            'response': response
        })
    except Exception as e:
        print(f"Chatbot error: {str(e)}")  # Add logging
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

from django.shortcuts import render

def chatbot_page(request):
    return render(request, "index.html")