from django.contrib import admin
from .models import MediaItem

@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'media_type', 'release_date', 'created_at')
    list_filter = ('media_type',)
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
