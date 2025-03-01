from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Q
from resources.models import Resource

class ResourceSearchService:
    @staticmethod
    def search(query, filters=None):
        if not filters:
            filters = {}

        # Base query
        search_query = SearchQuery(query)
        
        # Create search vector
        vector = SearchVector('title', weight='A') + \
                 SearchVector('description', weight='B') + \
                 SearchVector('tags', weight='B') + \
                 SearchVector('resource_type', weight='C')

        # Start with all resources
        queryset = Resource.objects.filter(is_approved=True)

        # Apply search if query exists
        if query:
            queryset = queryset.annotate(
                rank=SearchRank(vector, search_query)
            ).filter(rank__gte=0.1).order_by('-rank')

        # Apply filters
        if filters.get('resource_type'):
            queryset = queryset.filter(resource_type=filters['resource_type'])
        
        if filters.get('difficulty_level'):
            queryset = queryset.filter(difficulty_level=filters['difficulty_level'])
        
        if filters.get('category'):
            queryset = queryset.filter(category__slug=filters['category'])

        return queryset 