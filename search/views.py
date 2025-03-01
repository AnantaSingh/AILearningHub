from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .services import ResourceSearchService
from resources.models import Category, Resource
from django.db.models import Q
from resources.services.search_service import AIResourceSearchService
from bookmarks.models import Bookmark

# Create your views here.

class ResourceSearchView(TemplateView):
    template_name = 'search/search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        
        if query:
            search_service = AIResourceSearchService()
            results = search_service.search_all(query)
            
            # Get all admin-saved URLs
            admin_saved_urls = set(
                Bookmark.objects.filter(is_admin_saved=True)
                .values_list('url', flat=True)
            )
            
            # Check bookmarks
            if self.request.user.is_authenticated:
                bookmarked_urls = set(
                    Bookmark.objects.filter(
                        user=self.request.user,
                        is_bookmarked=True
                    ).values_list('url', flat=True)
                )
                
                for result in results:
                    result['is_bookmarked'] = result['url'] in bookmarked_urls
                    result['is_saved_to_db'] = result['url'] in admin_saved_urls
            
            context['resources'] = results
        else:
            context['resources'] = []
            
        context['query'] = query
        return context

class ResourceSearchViewOld(ListView):
    template_name = 'search/search_results.html'
    context_object_name = 'resources'
    paginate_by = 10

    def get_queryset(self):
        queryset = Resource.objects.filter(is_approved=True)
        query = self.request.GET.get('q', '')
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__icontains=query)
            )

        # Add filters
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)

        resource_type = self.request.GET.get('type')
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': Category.objects.all(),
            'query': self.request.GET.get('q', ''),
            'resource_types': Resource.RESOURCE_TYPES,
            'selected_category': self.request.GET.get('category', ''),
            'selected_type': self.request.GET.get('type', '')
        })
        return context

def search_view(request):
    query = request.GET.get('q', '')
    local_query = request.GET.get('local_q', '')
    
    # Your existing API search code here
    resources = []  # Your API results
    
    # Add local search if local_query exists
    local_results = []
    if local_query:
        local_results = Bookmark.objects.filter(
            Q(title__icontains=local_query) |
            Q(description__icontains=local_query) |
            Q(source__icontains=local_query)
        ).distinct()

    return render(request, 'search/search_results.html', {
        'query': query,
        'local_query': local_query,
        'resources': resources,
        'local_results': local_results,
    })

def local_search_view(request):
    query = request.GET.get('q', '')
    local_results = []
    
    if query:
        # Get all admin saved items
        local_results = Bookmark.objects.filter(
            is_admin_saved=True
        ).filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(source__icontains=query)
        ).distinct()

        # If user is authenticated, check which results are bookmarked
        if request.user.is_authenticated:
            bookmarked_urls = set(
                Bookmark.objects.filter(
                    user=request.user,
                    is_bookmarked=True
                ).values_list('url', flat=True)
            )
            
            # Add is_bookmarked flag to each result
            for result in local_results:
                result.is_bookmarked = result.url in bookmarked_urls

    # Group results by source
    github_results = [r for r in local_results if r.source == 'GitHub']
    arxiv_results = [r for r in local_results if r.source == 'arXiv']
    other_results = [r for r in local_results if r.source not in ['GitHub', 'arXiv']]

    return render(request, 'search/local_search.html', {
        'query': query,
        'github_results': github_results,
        'arxiv_results': arxiv_results,
        'other_results': other_results,
        'total_count': len(local_results)
    })
