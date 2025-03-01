from django.contrib import admin
from .models import Category, Resource

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'resource_type', 'created_at', 'is_approved')
    list_filter = ('category', 'resource_type', 'is_approved')
    search_fields = ('title', 'description')
