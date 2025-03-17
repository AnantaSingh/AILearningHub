from django.shortcuts import render
import logging
from django.core.paginator import Paginator
from resources.models import Resource, Category
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from bookmarks.models import Bookmark

logger = logging.getLogger(__name__)

# Create your views here.

def home(request):
    return render(request, 'home.html')

def ai_resources(request):
    return render(request, 'core/ai_resources.html')

def communities(request):
    return render(request, 'core/communities.html')

def ai_handbooks(request):
    return render(request, 'core/ai_handbooks.html')

def research_papers(request):
    # Debug: Log all bookmarks
    all_bookmarks = Bookmark.objects.filter(is_admin_saved=True)
    logger.debug(f"Total admin-saved bookmarks: {all_bookmarks.count()}")
    for bookmark in all_bookmarks:
        logger.debug(f"Bookmark: {bookmark.title}")
        logger.debug(f"  Source: {bookmark.source}")
        logger.debug(f"  URL: {bookmark.url}")
        logger.debug("  ---")

    # Get all research papers (from arXiv and PapersWithCode)
    papers = Bookmark.objects.filter(
        is_admin_saved=True,
        source__in=['arXiv', 'PapersWithCode']
    ).order_by('-created_at')

    # Debug: Log filtered papers
    logger.debug(f"\nFiltered papers count: {papers.count()}")
    for paper in papers:
        logger.debug(f"Paper: {paper.title}")
        logger.debug(f"  Source: {paper.source}")
        logger.debug("  ---")

    # Get search query
    query = request.GET.get('q', '')
    if query:
        papers = papers.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )
        logger.debug(f"\nAfter search filter: {papers.count()} papers")

    # Get category filter
    category = request.GET.get('category')
    if category:
        papers = papers.filter(source=category)
        logger.debug(f"\nAfter category filter: {papers.count()} papers")

    # Get categories for sidebar
    categories = Bookmark.objects.filter(
        is_admin_saved=True,
        source__in=['arXiv', 'PapersWithCode']
    ).values('source').annotate(
        paper_count=Count('id')
    ).order_by('source')

    logger.debug(f"\nCategories with papers: {categories.count()}")
    for cat in categories:
        logger.debug(f"Category: {cat['source']} - {cat['paper_count']} papers")

    # Pagination
    paginator = Paginator(papers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'papers': page_obj,
        'query': query,
        'categories': categories,
        'selected_category': category,
        'total_papers': papers.count(),
    }
    
    return render(request, 'core/research_papers.html', context)

