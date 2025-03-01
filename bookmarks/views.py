from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from resources.models import Resource
from .models import Bookmark
import json

# Create your views here.

@require_POST
@login_required
def toggle_bookmark(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    try:
        data = json.loads(request.body)
        print("Received data for bookmark:", json.dumps(data, indent=2))  # Pretty print the data

        # Check if bookmark exists
        bookmark = Bookmark.objects.filter(
            user=request.user,
            url=data['url']
        ).first()

        if bookmark:
            print(f"Deleting bookmark {bookmark.id}")
            bookmark.delete()
            return JsonResponse({'status': 'removed'})

        # Create new bookmark with metadata
        metadata = {
            'stars': data.get('metadata', {}).get('stars', ''),
            'language': data.get('metadata', {}).get('language', ''),
            'authors': data.get('metadata', {}).get('authors', ''),
            'published': data.get('metadata', {}).get('published', '')
        }
        
        bookmark = Bookmark.objects.create(
            user=request.user,
            url=data['url'],
            title=data['title'],
            description=data['description'],
            resource_type=data['resource_type'],
            source=data['source'],
            metadata=metadata
        )
        print(f"Created bookmark {bookmark.id} with metadata:", json.dumps(metadata, indent=2))
        return JsonResponse({'status': 'added'})

    except Exception as e:
        print(f"Error saving bookmark: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def bookmark_list(request):
    bookmarks = Bookmark.objects.filter(user=request.user).order_by('-created_at')
    print(f"Found {bookmarks.count()} bookmarks for user {request.user.username}")
    return render(request, 'bookmarks/list.html', {'bookmarks': bookmarks})

@require_POST
@login_required
def add_bookmark(request):
    title = request.POST.get('title')
    url = request.POST.get('url')
    description = request.POST.get('description')
    resource_type = request.POST.get('resource_type')
    source = request.POST.get('source')
    metadata = request.POST.get('metadata', '{}')

    bookmark, created = Bookmark.objects.get_or_create(
        user=request.user,
        url=url,
        defaults={
            'title': title,
            'description': description,
            'resource_type': resource_type,
            'source': source,
            'metadata': metadata
        }
    )

    return JsonResponse({
        'status': 'created' if created else 'exists',
        'bookmark_id': bookmark.id
    })
