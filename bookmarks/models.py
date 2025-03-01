from django.db import models
from django.contrib.auth.models import User

class Bookmark(models.Model):
    RESOURCE_TYPES = (
        ('GITHUB', 'GitHub Repository'),
        ('PAPER', 'Research Paper'),
        ('TUTORIAL', 'Tutorial'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    url = models.URLField()
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=50)  # 'GitHub', 'arXiv', etc.
    
    # Additional metadata
    metadata = models.JSONField(default=dict)  # Store stars, forks, authors, etc.
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('user', 'url')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"
