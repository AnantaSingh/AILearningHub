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
    try:
        data = json.loads(request.body)
        print("Received data:", data)  # Debug print

        # Check if bookmark exists
        bookmark = Bookmark.objects.filter(
            user=request.user,
            url=data['url']
        ).first()

        if bookmark:
            print(f"Deleting bookmark {bookmark.id}")  # Debug print
            bookmark.delete()
            return JsonResponse({'status': 'removed'})

        # Create new bookmark
        bookmark = Bookmark.objects.create(
            user=request.user,
            url=data['url'],
            title=data['title'],
            description=data['description'],
            resource_type=data['resource_type'],
            source=data['source']
        )
        print(f"Created bookmark {bookmark.id}")  # Debug print
        return JsonResponse({'status': 'added'})

    except Exception as e:
        print(f"Error: {str(e)}")  # Debug print
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
