from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .services import ResourceSearchService
from resources.models import Category, Resource
from django.db.models import Q
from resources.services.search_service import AIResourceSearchService

# Create your views here.

class ResourceSearchView(TemplateView):
    template_name = 'search/search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        
        if query:
            search_service = AIResourceSearchService()
            results = search_service.search_all(query)
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
