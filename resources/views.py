from django.shortcuts import render
from django.http import JsonResponse
from github import Github
from django.conf import settings
import logging
from django.core.cache import cache
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
import json
from bookmarks.models import Bookmark
from .models import SavedResource

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
            bookmark.save()
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
