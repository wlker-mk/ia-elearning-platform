from django.contrib import admin
from .models import SearchIndexModel, SearchTrackingModel


@admin.register(SearchIndexModel)
class SearchIndexAdmin(admin.ModelAdmin):
    list_display = ['title', 'entity_type', 'entity_id', 'language', 'created_at', 'updated_at']
    list_filter = ['entity_type', 'language', 'created_at']
    search_fields = ['title', 'content', 'entity_id', 'keywords']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Entity Information', {
            'fields': ('entity_type', 'entity_id')
        }),
        ('Content', {
            'fields': ('title', 'content', 'keywords', 'language')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Prevent manual addition through admin (use API)
        return False


@admin.register(SearchTrackingModel)
class SearchTrackingAdmin(admin.ModelAdmin):
    list_display = ['query', 'result_count', 'latency_ms', 'created_at']
    list_filter = ['created_at']
    search_fields = ['query']
    readonly_fields = ['id', 'query', 'result_count', 'latency_ms', 'created_at']
    
    def has_add_permission(self, request):
        # Prevent manual addition (automatically tracked)
        return False
    
    def has_change_permission(self, request, obj=None):
        # Read-only
        return False