from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Resource(models.Model):
    RESOURCE_TYPES = (
        ('TUTORIAL', 'Tutorial'),
        ('COURSE', 'Course'),
        ('HANDBOOK', 'Handbook'),
        ('GITHUB', 'GitHub Repository'),
        ('PAPER', 'Research Paper'),
        ('BLOG', 'Blog Post'),
    )

    DIFFICULTY_LEVELS = [
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    url = models.URLField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_approved = models.BooleanField(default=False)
    
    # For GitHub repositories
    stars = models.IntegerField(null=True, blank=True)
    forks = models.IntegerField(null=True, blank=True)
    language = models.CharField(max_length=50, blank=True)

    # Add these new fields
    search_vector = SearchVectorField(null=True)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    difficulty_level = models.CharField(
        max_length=20,
        choices=DIFFICULTY_LEVELS,
        default='INTERMEDIATE'
    )
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    votes_count = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Resources"
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['resource_type']),
            models.Index(fields=['created_at']),
            GinIndex(fields=['search_vector']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Update search vector
        if not self.search_vector:
            self.search_vector = (
                f"{self.title} {self.description} {self.tags} "
                f"{self.get_resource_type_display()} {self.get_difficulty_level_display()}"
            )
        super().save(*args, **kwargs)
