from django.contrib.auth import views as auth_views
from accounts import views as account_views

urlpatterns = [
    # ... your existing URLs ...
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('signup/', account_views.signup_view, name='signup'),
] 