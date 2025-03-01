from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from resources.models import Category, Resource

class Command(BaseCommand):
    help = 'Populate database with sample AI resources'

    def handle(self, *args, **kwargs):
        # Create categories
        categories = {
            'machine-learning': 'Machine Learning',
            'deep-learning': 'Deep Learning',
            'nlp': 'Natural Language Processing',
            'computer-vision': 'Computer Vision',
            'reinforcement-learning': 'Reinforcement Learning'
        }

        for slug, name in categories.items():
            Category.objects.get_or_create(
                slug=slug,
                name=name,
                description=f"Resources related to {name}"
            )

        # Get categories for reference
        ml_category = Category.objects.get(slug='machine-learning')
        dl_category = Category.objects.get(slug='deep-learning')
        nlp_category = Category.objects.get(slug='nlp')

        # Create sample resources
        resources_data = [
            {
                'title': 'Machine Learning Crash Course',
                'description': 'Google\'s fast-paced, practical introduction to machine learning',
                'url': 'https://developers.google.com/machine-learning/crash-course',
                'category': ml_category,
                'resource_type': 'COURSE',
                'tags': 'machine learning, basics, google',
                'difficulty_level': 'BEGINNER'
            },
            {
                'title': 'Deep Learning Specialization',
                'description': 'Deep Learning specialization by Andrew Ng on Coursera',
                'url': 'https://www.coursera.org/specializations/deep-learning',
                'category': dl_category,
                'resource_type': 'COURSE',
                'tags': 'deep learning, neural networks, coursera',
                'difficulty_level': 'INTERMEDIATE'
            },
            {
                'title': 'Hugging Face Transformers',
                'description': 'State-of-the-art Natural Language Processing library',
                'url': 'https://github.com/huggingface/transformers',
                'category': nlp_category,
                'resource_type': 'GITHUB',
                'tags': 'nlp, transformers, python',
                'difficulty_level': 'ADVANCED',
                'stars': 12000,
                'forks': 2800,
                'language': 'Python'
            },
            # Add more resources as needed
        ]

        # Get or create a default author
        author, _ = User.objects.get_or_create(
            username='admin',
            defaults={'is_staff': True, 'is_superuser': True}
        )

        # Create resources
        for data in resources_data:
            Resource.objects.get_or_create(
                title=data['title'],
                defaults={
                    'description': data['description'],
                    'url': data['url'],
                    'category': data['category'],
                    'resource_type': data['resource_type'],
                    'tags': data['tags'],
                    'difficulty_level': data['difficulty_level'],
                    'author': author,
                    'is_approved': True,
                    'stars': data.get('stars'),
                    'forks': data.get('forks'),
                    'language': data.get('language', '')
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated database with sample data')) 