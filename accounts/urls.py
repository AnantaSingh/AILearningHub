from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
] 