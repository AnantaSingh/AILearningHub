from django.shortcuts import render
from django.http import JsonResponse
from github import Github
from django.conf import settings
import logging
from django.core.cache import cache

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
