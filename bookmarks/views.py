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
        print("Received bookmark data:", data)
        
        # Map source to resource_type
        source_to_type = {
            'GitHub': 'GITHUB',
            'arXiv': 'PAPER',
            'PapersWithCode': 'PAPER',
            'Coursera': 'COURSE'
        }
        resource_type = source_to_type.get(data.get('source', ''), 'GITHUB')
        
        # Check if bookmark exists
        bookmark = Bookmark.objects.filter(
            user=request.user,
            url=data['url']
        ).first()
        
        if bookmark:
            print("Found existing bookmark:", bookmark.source)
            if bookmark.is_admin_saved:
                # If admin saved, just toggle bookmark flag
                bookmark.is_bookmarked = not bookmark.is_bookmarked
                bookmark.save()
            else:
                # If only bookmarked, delete it
                bookmark.delete()
            
            return JsonResponse({'status': 'success', 'action': 'removed'})
        else:
            print("Creating new bookmark with source:", data.get('source'))
            # Create new bookmark with default values if data missing
            bookmark = Bookmark.objects.create(
                user=request.user,
                url=data['url'],
                title=data.get('title', ''),
                description=data.get('description', ''),
                source=data.get('source', ''),
                resource_type=resource_type,  # Add the mapped resource_type
                metadata=data.get('metadata', {}),
                is_bookmarked=True,
                is_admin_saved=False
            )
            print("Created bookmark with source:", bookmark.source)
            return JsonResponse({'status': 'success', 'action': 'added'})
            
    except Exception as e:
        print(f"Error in toggle_bookmark: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def bookmark_list(request):
    # Only show items that are actually bookmarked by user
    bookmarks = Bookmark.objects.filter(
        user=request.user,
        is_bookmarked=True  # Add this condition
    ).order_by('-created_at')
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
