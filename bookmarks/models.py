from django.db import models
from django.contrib.auth.models import User

class Bookmark(models.Model):
    RESOURCE_TYPES = [
        ('GITHUB', 'GitHub Repository'),
        ('PAPER', 'Research Paper'),
        ('COURSE', 'Online Course'),
        ('BLOG', 'Blog Post'),
        ('COMMUNITY', 'Community Resource'),
        ('DOCUMENTATION', 'Documentation'),
        ('BOOK', 'Book'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_bookmarks')
    resource = models.ForeignKey(
        'resources.Resource',
        on_delete=models.CASCADE,
        related_name='resource_bookmarks',
        null=True,  # Allow null initially for migration
        blank=True
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    url = models.URLField()
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=50)  # 'GitHub' or 'arXiv'
    metadata = models.JSONField(default=dict)  # For stars, authors, etc.
    is_bookmarked = models.BooleanField(default=True)  # For user bookmarks
    is_admin_saved = models.BooleanField(default=False)  # For admin DB saves

    class Meta:
        unique_together = ('user', 'url')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"
