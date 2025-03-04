"""
URL configuration for ai_learning_hub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from resources.views import trending_repos, github_explorer_view, admin_portal
from django.contrib.auth import views as auth_views
from accounts.views import signup_view, CustomLogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('search/', include('search.urls')),
    path('accounts/', include('allauth.urls')),
    path('bookmarks/', include('bookmarks.urls')),
    path('api/github/trending/', trending_repos, name='trending_repos'),
    path('github-explorer/', github_explorer_view, name='github_explorer'),
    path('api/resources/', include('resources.urls')),
    path('admin-portal/', admin_portal, name='admin_portal'),
    path('chatbot/', include('chatbot.urls')),
    # Authentication URLs
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(
        template_name='registration/logged_out.html'
    ), name='logout'),
    path('accounts/signup/', signup_view, name='signup'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
