import requests
from github import Github
import arxiv
from django.conf import settings

class AIResourceSearchService:
    def __init__(self):
        self.github = Github(settings.GITHUB_ACCESS_TOKEN)

    def search_github(self, query):
        try:
            # Search AI-related repositories
            repositories = self.github.search_repositories(
                query=f'topic:artificial-intelligence {query}',
                sort='stars',
                order='desc'
            )
            return [{
                'title': repo.name,
                'description': repo.description or "No description available",
                'url': repo.html_url,
                'stars': repo.stargazers_count,
                'language': repo.language,
                'source': 'GitHub',
                'metadata': {
                    'stars': str(repo.stargazers_count),
                    'language': repo.language or ''
                }
            } for repo in repositories[:5]]
        except Exception as e:
            print(f"GitHub search error: {e}")
            return []

    def search_arxiv(self, query):
        try:
            # Search AI papers
            search = arxiv.Search(
                query=f"all:{query} AND (cat:cs.AI OR cat:cs.LG OR cat:cs.CL)",
                max_results=5,  # Top 5 papers
                sort_by=arxiv.SortCriterion.Relevance
            )
            return [{
                'title': paper.title,
                'description': paper.summary[:300] + "...",  # Truncate long summaries
                'url': paper.pdf_url,
                'authors': ', '.join([str(author) for author in paper.authors[:3]]),  # First 3 authors
                'published': paper.published.strftime("%Y-%m-%d"),
                'source': 'arXiv',
                'metadata': {
                    'authors': ', '.join([str(author) for author in paper.authors[:3]]),
                    'published': paper.published.strftime("%Y-%m-%d")
                }
            } for paper in search.results()]
        except Exception as e:
            print(f"arXiv search error: {e}")
            return []

    def search_all(self, query):
        if not query:
            return []
            
        results = []
        # Combine results from different sources
        results.extend(list(self.search_github(query)))
        results.extend(list(self.search_arxiv(query)))
        return results 