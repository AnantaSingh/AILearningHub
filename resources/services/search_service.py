import requests
from github import Github
import arxiv
from django.conf import settings
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class AIResourceSearchService:
    def __init__(self):
        self.github = Github(settings.GITHUB_ACCESS_TOKEN)

    def search_github(self, query):
        try:
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
            logger.error(f"GitHub search error: {e}")
            return []

    def search_arxiv(self, query):
        try:
            # Search AI papers
            search = arxiv.Search(
                query=f"all:{query} AND (cat:cs.AI OR cat:cs.LG OR cat:cs.CL)",
                max_results=5,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            return [{
                'title': paper.title,
                'description': paper.summary[:300] + "...",
                'url': paper.pdf_url,
                'authors': ', '.join([str(author) for author in paper.authors[:3]]),
                'published': paper.published.strftime("%Y-%m-%d"),
                'source': 'arXiv',
                'metadata': {
                    'authors': ', '.join([str(author) for author in paper.authors[:3]]),
                    'published': paper.published.strftime("%Y-%m-%d")
                }
            } for paper in search.results()]
        except Exception as e:
            logger.error(f"arXiv search error: {e}")
            return []

    def search_all(self, query, page=1):
        results = []
        
        # Fetch results from all sources
        try:
            github_results = self.search_github(query)
            results.extend(github_results)
        except Exception as e:
            logger.error(f"GitHub search error: {str(e)}")

        try:
            arxiv_results = self.search_arxiv(query)
            results.extend(arxiv_results)
        except Exception as e:
            logger.error(f"arXiv search error: {str(e)}")

        try:
            papers_with_code_results = self.search_papers_with_code(query, page)
            results.extend(papers_with_code_results)
        except Exception as e:
            logger.error(f"PapersWithCode search error: {str(e)}")

        try:
            course_results = self.search_courses(query)
            results.extend(course_results)
        except Exception as e:
            logger.error(f"Course search error: {str(e)}")

        try:
            blog_results = self.search_blogs(query)
            results.extend(blog_results)
        except Exception as e:
            logger.error(f"Blog search error: {str(e)}")

        return results

    def search_papers_with_code(self, query, page=1):
        """Search PapersWithCode API"""
        try:
            url = f"https://paperswithcode.com/api/v1/papers/search"
            response = requests.get(url, params={'q': query})
            results = []
            
            if response.ok:
                data = response.json()
                for paper in data.get('results', [])[:10]:  # Increased to 10 results
                    # Extract first 3 authors if available
                    authors = paper.get('authors', [])
                    author_names = ', '.join([author.get('name', '') for author in authors[:3]])
                    
                    results.append({
                        'title': paper.get('title', ''),
                        'description': paper.get('abstract', '')[:300] + "..." if paper.get('abstract') else '',
                        'url': f"https://paperswithcode.com{paper.get('url', '')}",
                        'source': 'PapersWithCode',
                        'authors': author_names,
                        'published': paper.get('published', '').split('T')[0] if paper.get('published') else '',
                        'github_url': paper.get('repository_url', ''),
                        'paper_url': paper.get('paper_url', ''),
                        'metadata': {
                            'authors': author_names,
                            'published': paper.get('published', '').split('T')[0] if paper.get('published') else '',
                            'github_url': paper.get('repository_url', '')
                        }
                    })
            return results
        except Exception as e:
            logger.error(f"PapersWithCode search error: {str(e)}")
            return []

    def search_courses(self, query):
        """Search for AI courses using Coursera API"""
        try:
            # Coursera API endpoint
            url = "https://api.coursera.org/api/courses.v1"
            
            # Parameters for the API request
            params = {
                'q': f"search",
                'query': f"{query} AI artificial intelligence machine learning",
                'fields': 'name,description,partnerLogo,instructorIds,partnerIds,photoUrl,specializations',
                'includes': 'instructorIds,partnerIds,specializations',
                'limit': 5  # Limit to 5 results
            }
            
            response = requests.get(url, params=params)
            results = []
            
            if response.ok:
                data = response.json()
                courses = data.get('elements', [])
                
                for course in courses:
                    results.append({
                        'title': course.get('name', ''),
                        'description': course.get('description', '')[:300] + "..." if course.get('description') else '',
                        'url': f"https://www.coursera.org/learn/{course.get('slug', '')}",
                        'source': 'Coursera',
                        'platform': 'Coursera',
                        'image_url': course.get('photoUrl', ''),
                        'metadata': {
                            'platform': 'Coursera',
                            'partner': course.get('partnerName', ''),
                            'specialization': course.get('specializationName', '')
                        }
                    })
                
            return results
        except Exception as e:
            logger.error(f"Coursera API search error: {str(e)}")
            return []

    def search_blogs(self, query):
        """Search AI blogs and communities"""
        blog_sources = [
            {
                'name': 'Towards Data Science',
                'url': f'https://towardsdatascience.com/search?q={query}',
                'type': 'BLOG'
            },
            {
                'name': 'OpenAI Blog',
                'url': f'https://openai.com/blog?q={query}',
                'type': 'BLOG'
            },
            {
                'name': 'Reddit r/MachineLearning',
                'url': f'https://www.reddit.com/r/MachineLearning/search/?q={query}',
                'type': 'COMMUNITY'
            }
        ]
        
        results = []
        # Implementation would need to handle each source's specific scraping/API
        # This is a placeholder for demonstration
        return results

    def search_documentation(self, query):
        """Search AI documentation and handbooks"""
        doc_sources = [
            {
                'name': 'Deep Learning Book',
                'url': 'https://www.deeplearningbook.org/',
                'type': 'BOOK'
            },
            {
                'name': 'Stanford CS229',
                'url': 'https://cs229.stanford.edu/notes/',
                'type': 'COURSE_NOTES'
            }
        ]
        
        results = []
        # Implementation would need specific handling for each source
        return results 