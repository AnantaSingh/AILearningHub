from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    path('github/trending/', views.trending_repos, name='trending_repos'),
    path('resources/save/', views.save_resource, name='save_resource'),
    path('github-explorer/', views.github_explorer_view, name='github_explorer'),
    path('submit/', views.submit_resource, name='submit_resource'),
    path('my-submissions/', views.my_submissions, name='my_submissions'),
    path('pending-approvals/', views.pending_approvals, name='pending_approvals'),
    path('approve/<int:resource_id>/', views.approve_resource, name='approve_resource'),
    # ... your other URLs
] 