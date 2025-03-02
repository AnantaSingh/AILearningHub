from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .services import ResourceSearchService
from resources.models import Category, Resource
from django.db.models import Q, Count
from resources.services.search_service import AIResourceSearchService
from bookmarks.models import Bookmark
import json  # Add this at the top

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
    selected_category = request.GET.get('category', '')
    local_results = []
    
    if query or selected_category:
        # Base query
        base_query = Bookmark.objects.filter(is_admin_saved=True)
        
        # Apply category filter if selected
        if selected_category:
            base_query = base_query.filter(source=selected_category)
        
        # Apply search filter if query exists
        if query:
            base_query = base_query.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(source__icontains=query)
            )
        
        local_results = base_query.distinct()

        # If user is authenticated, check which results are bookmarked
        if request.user.is_authenticated:
            bookmarked_urls = set(
                Bookmark.objects.filter(
                    user=request.user,
                    is_bookmarked=True
                ).values_list('url', flat=True)
            )
            
            for result in local_results:
                result.is_bookmarked = result.url in bookmarked_urls
                # Ensure metadata is properly formatted for all resource types
                if result.metadata:
                    if result.source == 'Coursera':
                        result.metadata_json = json.dumps({
                            'platform': result.metadata.get('platform', ''),
                            'partner': result.metadata.get('partner', ''),
                            'specialization': result.metadata.get('specialization', ''),
                            'image_url': result.metadata.get('image_url', '')
                        })
                    elif result.source in ['arXiv', 'PapersWithCode']:
                        result.metadata_json = json.dumps({
                            'authors': result.metadata.get('authors', ''),
                            'published': result.metadata.get('published', ''),
                            'github_url': result.metadata.get('github_url', '')
                        })
                    else:  # GitHub
                        result.metadata_json = json.dumps({
                            'stars': result.metadata.get('stars', ''),
                            'language': result.metadata.get('language', '')
                        })

    # Get category counts for the sidebar
    category_counts = Bookmark.objects.filter(is_admin_saved=True).values('source').annotate(
        count=Count('id')
    ).order_by('source')

    # Get specific counts
    github_count = sum(c['count'] for c in category_counts if c['source'] == 'GitHub')
    paper_count = sum(c['count'] for c in category_counts if c['source'] in ['arXiv', 'PapersWithCode'])
    course_count = sum(c['count'] for c in category_counts if c['source'] == 'Coursera')

    # Separate results by source
    github_results = [r for r in local_results if r.source == 'GitHub']
    paper_results = [r for r in local_results if r.source in ['arXiv', 'PapersWithCode']]
    course_results = [r for r in local_results if r.source == 'Coursera']

    return render(request, 'search/local_search.html', {
        'query': query,
        'selected_category': selected_category,
        'github_results': github_results,
        'paper_results': paper_results,
        'course_results': course_results,
        'total_count': len(local_results),
        'github_count': github_count,
        'paper_count': paper_count,
        'course_count': course_count,
        'category_counts': category_counts,
    })
