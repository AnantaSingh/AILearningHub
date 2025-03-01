from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.ResourceSearchView.as_view(), name='search'),
    path('local/', views.local_search_view, name='local_search'),
] 