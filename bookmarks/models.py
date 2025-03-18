from django.db import models
from django.contrib.auth.models import User
from resources.models import Resource

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
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='bookmarks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)  # Make description optional
    url = models.URLField()
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=50, blank=True)  # Make source optional
    metadata = models.JSONField(default=dict, blank=True)  # Make metadata optional
    is_bookmarked = models.BooleanField(default=True)  # For user bookmarks
    is_admin_saved = models.BooleanField(default=False)  # For admin DB saves

    class Meta:
        unique_together = ('user', 'resource')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def save(self, *args, **kwargs):
        # If this is a new bookmark, copy data from resource
        if not self.pk and self.resource:
            self.title = self.resource.title
            self.description = self.resource.description
            self.url = self.resource.url
            self.resource_type = self.resource.resource_type
        super().save(*args, **kwargs)
