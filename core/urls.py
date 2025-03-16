from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('ai_resources/', views.ai_resources, name='ai_resources'),
    path('research_papers/', views.research_papers, name='research_papers'),
] 