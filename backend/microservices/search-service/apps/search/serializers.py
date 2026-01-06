from rest_framework import serializers
from typing import List, Optional

class BaseSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class SearchIndexSerializer(BaseSerializer):
    """Serializer for SearchIndex model"""
    entity_type = serializers.CharField(max_length=100)
    entity_id = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=500)
    content = serializers.CharField()
    keywords = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        default=list
    )
    language = serializers.CharField(max_length=10, required=False, allow_null=True)

    def validate_keywords(self, value):
        """Ensure keywords is a list"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Keywords must be a list")
        return value


class SearchIndexCreateSerializer(serializers.Serializer):
    """Serializer for creating search index entries"""
    entity_type = serializers.CharField(max_length=100)
    entity_id = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=500)
    content = serializers.CharField()
    keywords = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        default=list
    )
    language = serializers.CharField(max_length=10, required=False, allow_null=True, default='en')


class SearchIndexUpdateSerializer(serializers.Serializer):
    """Serializer for updating search index entries"""
    title = serializers.CharField(max_length=500, required=False)
    content = serializers.CharField(required=False)
    keywords = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False
    )
    language = serializers.CharField(max_length=10, required=False, allow_null=True)


class SearchTrackingSerializer(BaseSerializer):
    """Serializer for SearchTracking model"""
    query = serializers.CharField(max_length=500)
    result_count = serializers.IntegerField(min_value=0)
    latency_ms = serializers.IntegerField(min_value=0)


class SearchQuerySerializer(serializers.Serializer):
    """Serializer for search query parameters"""
    q = serializers.CharField(required=True, min_length=1, max_length=500)
    entity_type = serializers.CharField(required=False, allow_null=True)
    language = serializers.CharField(max_length=10, required=False, allow_null=True)
    limit = serializers.IntegerField(min_value=1, max_value=100, default=20)
    offset = serializers.IntegerField(min_value=0, default=0)


class SearchResultSerializer(serializers.Serializer):
    """Serializer for search results"""
    results = SearchIndexSerializer(many=True)
    total = serializers.IntegerField()
    query = serializers.CharField()
    limit = serializers.IntegerField()
    offset = serializers.IntegerField()
    latency_ms = serializers.IntegerField()


class BulkIndexSerializer(serializers.Serializer):
    """Serializer for bulk indexing"""
    items = SearchIndexCreateSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Items list cannot be empty")
        if len(value) > 1000:
            raise serializers.ValidationError("Cannot index more than 1000 items at once")
        return value


class SearchStatsSerializer(serializers.Serializer):
    """Serializer for search statistics"""
    total_searches = serializers.IntegerField()
    avg_latency_ms = serializers.FloatField()
    total_indexed_items = serializers.IntegerField()
    top_queries = serializers.ListField(
        child=serializers.DictField()
    )