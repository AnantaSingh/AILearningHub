from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Explicitly use ModelBackend for authentication
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('core:home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

class CustomLogoutView(LoginRequiredMixin, View):
    """Custom logout view that handles both GET and POST requests"""
    
    def get(self, request, *args, **kwargs):
        """Handle GET requests by logging out the user"""
        logout(request)
        return redirect('core:home')
        
    def post(self, request, *args, **kwargs):
        """Handle POST requests by logging out the user"""
        logout(request)
        return redirect('core:home') 