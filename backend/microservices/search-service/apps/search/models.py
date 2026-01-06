from django.db import models
import uuid

class SearchIndexModel(models.Model):
    """Django model mirror of Prisma SearchIndex for Django admin"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(max_length=100, db_index=True)
    entity_id = models.CharField(max_length=100, db_index=True)
    title = models.CharField(max_length=500)
    content = models.TextField()
    keywords = models.JSONField(default=list)
    language = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'search_index'
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.entity_type} - {self.title}"


class SearchTrackingModel(models.Model):
    """Django model mirror of Prisma SearchTracking for Django admin"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    query = models.CharField(max_length=500)
    result_count = models.IntegerField()
    latency_ms = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'search_tracking'
        ordering = ['-created_at']

    def __str__(self):
        return f"Query: {self.query} ({self.result_count} results)"