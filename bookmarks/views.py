from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from resources.models import Resource
from .models import Bookmark

# Create your views here.

@require_POST
@login_required
def toggle_bookmark(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    bookmark, created = Bookmark.objects.get_or_create(
        user=request.user,
        resource=resource
    )
    
    if not created:
        bookmark.delete()
        return JsonResponse({'status': 'removed'})
    
    return JsonResponse({'status': 'added'})

@login_required
def bookmark_list(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('resource')
    return render(request, 'bookmarks/bookmark_list.html', {'bookmarks': bookmarks})

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
