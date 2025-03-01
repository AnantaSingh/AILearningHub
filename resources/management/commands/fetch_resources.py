from django.core.management.base import BaseCommand
from resources.services.fetchers import GithubFetcher, ArxivFetcher, TutorialFetcher
from resources.models import Resource, Category
from django.db import transaction

class Command(BaseCommand):
    help = 'Fetch AI resources from various sources'

    def handle(self, *args, **kwargs):
        # Initialize fetchers
        github_fetcher = GithubFetcher()
        arxiv_fetcher = ArxivFetcher()
        tutorial_fetcher = TutorialFetcher()

        with transaction.atomic():
            # Fetch GitHub repositories
            for repo_data in github_fetcher.fetch_ai_repositories():
                category, _ = Category.objects.get_or_create(
                    slug='github-projects',
                    defaults={'name': 'GitHub Projects'}
                )
                Resource.objects.update_or_create(
                    url=repo_data['url'],
                    defaults={
                        'title': repo_data['title'],
                        'description': repo_data['description'],
                        'category': category,
                        'resource_type': 'GITHUB',
                        'stars': repo_data['stars'],
                        'forks': repo_data['forks'],
                        'language': repo_data['language'],
                        'tags': repo_data['tags'],
                        'is_approved': True
                    }
                )

            # Fetch arXiv papers
            for paper_data in arxiv_fetcher.fetch_ai_papers():
                category, _ = Category.objects.get_or_create(
                    slug='research-papers',
                    defaults={'name': 'Research Papers'}
                )
                Resource.objects.update_or_create(
                    url=paper_data['url'],
                    defaults={
                        'title': paper_data['title'],
                        'description': paper_data['description'],
                        'category': category,
                        'resource_type': 'PAPER',
                        'tags': paper_data['tags'],
                        'is_approved': True
                    }
                )

        self.stdout.write(self.style.SUCCESS('Successfully fetched resources')) 