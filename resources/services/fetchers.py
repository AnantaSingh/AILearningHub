import requests
from github import Github
import arxiv
from bs4 import BeautifulSoup
from django.conf import settings
from resources.models import Resource, Category

class GithubFetcher:
    def __init__(self):
        self.github = Github(settings.GITHUB_ACCESS_TOKEN)

    def fetch_ai_repositories(self):
        # Search for AI-related repositories
        queries = ['artificial-intelligence', 'machine-learning', 'deep-learning']
        for query in queries:
            repositories = self.github.search_repositories(
                query=f'topic:{query}',
                sort='stars',
                order='desc'
            )
            for repo in repositories[:10]:  # Top 10 repos per query
                yield {
                    'title': repo.name,
                    'description': repo.description,
                    'url': repo.html_url,
                    'resource_type': 'GITHUB',
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count,
                    'language': repo.language,
                    'tags': ', '.join(repo.get_topics())
                }

class ArxivFetcher:
    def fetch_ai_papers(self):
        # Search for recent AI papers
        search = arxiv.Search(
            query="cat:cs.AI OR cat:cs.LG",
            max_results=50,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        for paper in search.results():
            yield {
                'title': paper.title,
                'description': paper.summary,
                'url': paper.pdf_url,
                'resource_type': 'PAPER',
                'tags': ', '.join(paper.categories),
                'author': paper.authors[0] if paper.authors else None
            }

class TutorialFetcher:
    def fetch_tutorials(self):
        # Example sources
        sources = [
            'https://www.coursera.org/courses?query=artificial%20intelligence',
            'https://www.udacity.com/courses/all?search=ai',
            # Add more sources
        ]
        # Implementation would depend on each site's structure
        # You might need to handle rate limiting and robots.txt 