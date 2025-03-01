from django.urls import path
from . import views

app_name = 'bookmarks'

urlpatterns = [
    path('', views.bookmark_list, name='list'),
    path('toggle/', views.toggle_bookmark, name='toggle'),
] 