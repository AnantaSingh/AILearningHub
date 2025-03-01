from django.urls import path
from . import views

urlpatterns = [
    path('save/', views.save_to_db, name='save_to_db'),
    # ... your other URLs
] 