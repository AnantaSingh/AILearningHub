from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('ai_resources/', views.ai_resources, name='ai_resources'),
    path('research_papers/', views.research_papers, name='research_papers'),
    path('communities/', views.communities, name='communities'),
    path('ai_handbooks/', views.ai_handbooks, name='ai_handbooks'),
] 