from django.http import JsonResponse
from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)

def get_trending_repos(request):
    try:
        # GitHub API endpoint for searching repositories
        url = "https://api.github.com/search/repositories"
        
        # Parameters for trending repositories
        params = {
            'q': 'topic:artificial-intelligence created:>2024-01-01',
            'sort': 'stars',
            'order': 'desc',
            'per_page': 10
        }
        
        headers = {}
        if settings.GITHUB_ACCESS_TOKEN:
            headers['Authorization'] = f'token {settings.GITHUB_ACCESS_TOKEN}'
            logger.info("Using GitHub token for API request")
        else:
            logger.warning("No GitHub token found")

        logger.info(f"Making request to GitHub API: {url}")
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"Received {len(data.get('items', []))} repositories from GitHub")
        
        # Format the response
        repos = []
        for item in data.get('items', []):
            repos.append({
                'name': item['full_name'],
                'description': item['description'],
                'url': item['html_url'],
                'stars': item['stargazers_count'],
                'language': item['language'],
                'created_at': item['created_at']
            })
        
        return JsonResponse({
            'status': 'success',
            'data': repos
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"GitHub API request failed: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f"Failed to fetch repositories: {str(e)}"
        }, status=500)
    except Exception as e:
        logger.error(f"Unexpected error in get_trending_repos: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f"An unexpected error occurred: {str(e)}"
        }, status=500) 