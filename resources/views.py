from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from github import Github
from django.conf import settings
import logging
from django.core.cache import cache
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
import json
from bookmarks.models import Bookmark
from .models import SavedResource, Resource, Category
from .services.search_service import AIResourceSearchService
from django.contrib import messages
from django.urls import reverse

logger = logging.getLogger(__name__)

# Create your views here.

def trending_repos(request):
    try:
        # Try to get cached results first
        cache_key = 'github_trending_repos'
        cached_results = cache.get(cache_key)
        
        if cached_results:
            logger.info("Returning cached results")
            return JsonResponse(cached_results, safe=False)

        logger.info("Fetching fresh results from GitHub")
        g = Github(settings.GITHUB_ACCESS_TOKEN)
        
        # Simplified query focusing on most relevant results
        query = (
            "topic:artificial-intelligence "
            "language:python "
            "stars:>5000 "
            "fork:false"
        )
        
        # Reduce to 6 repositories
        repos = g.search_repositories(
            query=query,
            sort='stars',
            order='desc'
        )[:6]
        
        results = [{
            'name': repo.name,
            'description': repo.description,
            'url': repo.html_url,
            'stars': repo.stargazers_count,
            'language': repo.language,
            'source': 'GitHub'
        } for repo in repos]
        
        # Cache the results for 6 hours (21600 seconds)
        cache.set(cache_key, results, 21600)
        
        logger.info(f"Found {len(results)} repositories")
        return JsonResponse(results, safe=False)
        
    except Exception as e:
        logger.error(f"Error in trending_repos: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def github_explorer_view(request):
    return render(request, 'github_explorer.html')

@require_POST
@staff_member_required
def save_to_db(request):
    try:
        data = json.loads(request.body)
        url = data['url']
        
        # Check if bookmark exists
        bookmark = Bookmark.objects.filter(
            url=url,
            user=request.user
        ).first()
        
        if bookmark:
            # Toggle admin save flag
            bookmark.is_admin_saved = not bookmark.is_admin_saved
            
            # If removing from DB, also remove user bookmark
            if not bookmark.is_admin_saved:
                bookmark.is_bookmarked = False
            
            bookmark.save()
            
            # If neither flag is True, delete the record
            if not bookmark.is_admin_saved and not bookmark.is_bookmarked:
                bookmark.delete()
            
            return JsonResponse({
                'status': 'success', 
                'action': 'added' if bookmark.is_admin_saved else 'removed'
            })
        else:
            # Create new admin saved bookmark
            Bookmark.objects.create(
                user=request.user,
                url=url,
                title=data['title'],
                description=data['description'],
                source=data['source'],
                metadata=data['metadata'],
                resource_type='GITHUB' if data['source'] == 'GitHub' else 'PAPER',
                is_bookmarked=False,
                is_admin_saved=True
            )
            return JsonResponse({'status': 'success', 'action': 'added'})
            
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@staff_member_required
def admin_portal(request):
    query = request.GET.get('q', '')
    selected_source = request.GET.get('source', '')
    results = []
    
    if query:
        search_service = AIResourceSearchService()
        results = search_service.search_all(query)
        
        # Filter by source if selected
        if selected_source:
            results = [r for r in results if r['source'] == selected_source]
        
        # Get all admin-saved URLs
        admin_saved_urls = set(
            Bookmark.objects.filter(is_admin_saved=True)
            .values_list('url', flat=True)
        )
        
        # Add saved status to results
        for result in results:
            result['is_saved_to_db'] = result['url'] in admin_saved_urls

    # Count results by type
    github_count = len([r for r in results if r['source'] == 'GitHub'])
    papers_count = len([r for r in results if r['source'] in ['arXiv', 'PapersWithCode']])
    courses_count = len([r for r in results if r['source'] == 'Coursera'])

    return render(request, 'admin/portal.html', {
        'query': query,
        'resources': results,
        'selected_source': selected_source,
        'github_count': github_count,
        'papers_count': papers_count,
        'courses_count': courses_count,
    })

@login_required
@require_POST
def save_resource(request):
    try:
        data = json.loads(request.body)
        url = data.get('url')
        
        # Get or create resource
        resource = Resource.objects.get_or_create(
            url=url,
            defaults={
                'title': data.get('title', ''),
                'description': data.get('description', ''),
                'resource_type': data.get('resource_type', 'GITHUB'),
                'category': Category.objects.get_or_create(name='Uncategorized')[0],
                'author': request.user
            }
        )[0]

        # Create bookmark with is_bookmarked=False for admin saves
        bookmark = Bookmark.objects.create(
            user=request.user,
            resource=resource,
            title=data.get('title', ''),
            description=data.get('description', ''),
            url=url,
            resource_type=data.get('resource_type', 'GITHUB'),
            source=data.get('source', 'GITHUB'),
            is_bookmarked=False,  # Set to False for admin saves
            is_admin_saved=True
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Resource saved successfully',
            'resource_id': resource.id,
            'bookmark_id': bookmark.id
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
def submit_resource(request):
    if request.method == 'POST':
        try:
            category = Category.objects.get_or_create(
                name='Uncategorized',
                defaults={'slug': 'uncategorized'}
            )[0]
            
            # Map resource_type to correct source format
            resource_type = request.POST['resource_type']
            source_mapping = {
                'TUTORIAL': 'Tutorial',
                'COURSE': 'Course',
                'HANDBOOK': 'Handbook',
                'GITHUB': 'GitHub',
                'PAPER': 'Research Paper',
                'BLOG': 'Blog'
            }
            
            resource = Resource.objects.create(
                title=request.POST['title'],
                description=request.POST['description'],
                url=request.POST['url'],
                resource_type=resource_type,
                difficulty_level=request.POST['difficulty_level'],
                tags=request.POST['tags'],
                category=category,
                author=request.user,
                is_approved=False
            )

            # Create bookmark with proper source format
            Bookmark.objects.create(
                user=request.user,
                resource=resource,
                title=resource.title,
                description=resource.description,
                url=resource.url,
                resource_type=resource_type,
                source=source_mapping.get(resource_type, 'Other'),
                is_bookmarked=True,
                is_admin_saved=False
            )

            messages.success(request, 'Resource submitted successfully! It will be reviewed by an admin.')
            return redirect('resources:my_submissions')
        except Exception as e:
            messages.error(request, f'Error submitting resource: {str(e)}')
            return redirect('resources:submit_resource')
    
    return render(request, 'resources/submit.html')

@login_required
def my_submissions(request):
    submissions = Resource.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'resources/my_submissions.html', {
        'submissions': submissions
    })

@staff_member_required
def pending_approvals(request):
    # Get resources that are not approved and were submitted by users (not admin saved)
    pending_resources = Resource.objects.filter(
        is_approved=False,
        bookmarks__is_admin_saved=False  # Changed from True to False to show user submissions
    ).distinct().order_by('-created_at')
    
    return render(request, 'resources/pending_approvals.html', {
        'pending_resources': pending_resources
    })

@staff_member_required
@require_POST
def approve_resource(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    resource.is_approved = True
    resource.save()
    
    # Update the corresponding bookmark's admin_approved status
    Bookmark.objects.filter(
        resource=resource,
        is_admin_saved=False  # Changed from True to False to update user submissions
    ).update(is_admin_saved=True)  # Mark as admin approved
    
    messages.success(request, f'Resource "{resource.title}" has been approved.')
    return redirect('resources:pending_approvals')
