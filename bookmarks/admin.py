from django.contrib import admin
from .models import Bookmark

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'resource_type', 'created_at')
    list_filter = ('resource_type', 'is_bookmarked', 'is_admin_saved')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)

    def save_model(self, request, obj, form, change):
        if not obj.user:
            obj.user = request.user
        super().save_model(request, obj, form, change)
