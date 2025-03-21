from django.urls import path
from . import views
from . import api

app_name = 'resources'

urlpatterns = [
    # API endpoints
    path('api/github/trending/', api.get_trending_repos, name='github_trending'),
    path('save/', views.save_resource, name='save_resource'),
    
    # Views
    path('github-explorer/', views.github_explorer_view, name='github_explorer'),
    path('submit/', views.submit_resource, name='submit_resource'),
    path('my-submissions/', views.my_submissions, name='my_submissions'),
    path('pending-approvals/', views.pending_approvals, name='pending_approvals'),
    path('approve/<int:resource_id>/', views.approve_resource, name='approve_resource'),
    path('admin-portal/', views.admin_portal, name='admin_portal'),
    # ... your other URLs
] 