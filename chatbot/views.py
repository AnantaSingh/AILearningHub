from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
import json
from .chatbot import ChatBot

# Initialize the chatbot as a singleton
chatbot = ChatBot()

@cache_page(60 * 15)  # Cache the chat page for 15 minutes
def chat_page(request):
    """Render the chat interface"""
    return render(request, 'chatBot/chat.html')

@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """Handle chat API requests"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({
                'error': 'Message is required',
                'success': False
            }, status=400)
        
        # Get response from chatbot
        response = chatbot.get_response(user_message)
        
        return JsonResponse({
            'response': response,  # Changed to match original
            'success': True
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON format',
            'success': False
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'An error occurred: {str(e)}',
            'success': False
        }, status=500)