from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from resources.models import Resource, Category
from .models import Bookmark
import json

# Create your views here.

@login_required
@require_POST
def toggle_bookmark(request):
    try:
        data = json.loads(request.body)
        url = data.get('url')
        
        # First, handle potential duplicate resources
        existing_resources = Resource.objects.filter(url=url)
        if existing_resources.exists():
            # Use the first resource and delete others
            resource = existing_resources.first()
            # Update bookmarks to point to the first resource before deleting others
            Bookmark.objects.filter(resource__in=existing_resources.exclude(id=resource.id)).update(resource=resource)
            existing_resources.exclude(id=resource.id).delete()
        else:
            # Create new resource if none exists
            category = Category.objects.get_or_create(
                name='Uncategorized', 
                defaults={'slug': 'uncategorized'}
            )[0]
            
            resource = Resource.objects.create(
                url=url,
                title=data.get('title', ''),
                description=data.get('description', ''),
                resource_type=data.get('resource_type', 'GITHUB'),
                category=category,
                author=request.user
            )

        # Get or create bookmark
        bookmark = Bookmark.objects.filter(
            user=request.user,
            resource=resource
        ).first()

        if bookmark:
            # If bookmark exists, toggle is_bookmarked
            bookmark.is_bookmarked = not bookmark.is_bookmarked
            bookmark.save()
            message = "Bookmark removed" if not bookmark.is_bookmarked else "Bookmark added"
        else:
            # Create new bookmark
            bookmark = Bookmark.objects.create(
                user=request.user,
                resource=resource,
                title=data.get('title', ''),
                description=data.get('description', ''),
                url=url,
                resource_type=data.get('resource_type', 'GITHUB'),
                source=data.get('source', 'GITHUB'),
                is_bookmarked=True
            )
            message = "Bookmark added"

        print(f"Bookmark status: user={request.user.username}, url={url}, is_bookmarked={bookmark.is_bookmarked}")

        return JsonResponse({
            'status': 'success',
            'message': message,
            'is_bookmarked': bookmark.is_bookmarked
        })

    except Exception as e:
        print(f"Error in toggle_bookmark: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

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
