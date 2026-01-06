from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from asgiref.sync import async_to_sync
import logging

from .services import SearchService
from .serializers import (
    SearchIndexSerializer,
    SearchIndexCreateSerializer,
    SearchIndexUpdateSerializer,
    SearchQuerySerializer,
    SearchResultSerializer,
    SearchTrackingSerializer,
    BulkIndexSerializer,
    SearchStatsSerializer
)
from .permissions import IsOwnerOrReadOnly

logger = logging.getLogger(__name__)


class SearchIndexViewSet(viewsets.ViewSet):
    """ViewSet for managing search indexes"""
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = SearchService()
    
    def list(self, request):
        """List all indexed items with optional filtering"""
        try:
            entity_type = request.query_params.get('entity_type')
            limit = int(request.query_params.get('limit', 20))
            offset = int(request.query_params.get('offset', 0))
            
            async def get_items():
                async with self.service as svc:
                    if entity_type:
                        return await svc.get_all_by_type(entity_type, limit, offset)
                    else:
                        # Get all types
                        return await svc.get_all_by_type('course', limit, offset)
            
            result = async_to_sync(get_items)()
            return Response(result)
        except Exception as e:
            logger.error(f"Error listing indexes: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request):
        """Create a new search index entry"""
        serializer = SearchIndexCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data = serializer.validated_data
            
            async def create_index():
                async with self.service as svc:
                    return await svc.create_index(
                        entity_type=data['entity_type'],
                        entity_id=data['entity_id'],
                        title=data['title'],
                        content=data['content'],
                        keywords=data.get('keywords', []),
                        language=data.get('language', 'en')
                    )
            
            result = async_to_sync(create_index)()
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating index: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, pk=None):
        """Get a specific index entry"""
        try:
            async def get_index():
                async with self.service as svc:
                    # Try to get by ID first
                    all_items = await svc.db.searchindex.find_many(
                        where={'id': pk}
                    )
                    return all_items[0] if all_items else None
            
            result = async_to_sync(get_index)()
            if not result:
                return Response(
                    {'error': 'Index not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(self.service._format_index(result))
        except Exception as e:
            logger.error(f"Error retrieving index: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, pk=None):
        """Update an existing index entry"""
        serializer = SearchIndexUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data = serializer.validated_data
            
            async def update_index():
                async with self.service as svc:
                    return await svc.update_index(
                        index_id=pk,
                        **data
                    )
            
            result = async_to_sync(update_index)()
            if not result:
                return Response(
                    {'error': 'Index not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(result)
        except Exception as e:
            logger.error(f"Error updating index: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, pk=None):
        """Delete an index entry"""
        try:
            async def delete_index():
                async with self.service as svc:
                    return await svc.delete_index(pk)
            
            deleted = async_to_sync(delete_index)()
            if not deleted:
                return Response(
                    {'error': 'Index not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error deleting index: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def bulk_index(self, request):
        """Bulk create search indexes"""
        serializer = BulkIndexSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            items = serializer.validated_data['items']
            
            async def bulk_create():
                async with self.service as svc:
                    return await svc.bulk_index(items)
            
            result = async_to_sync(bulk_create)()
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error bulk indexing: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['delete'], url_path='entity/(?P<entity_type>[^/.]+)/(?P<entity_id>[^/.]+)')
    def delete_by_entity(self, request, entity_type=None, entity_id=None):
        """Delete all indexes for a specific entity"""
        try:
            async def delete_entity():
                async with self.service as svc:
                    return await svc.delete_by_entity(entity_type, entity_id)
            
            count = async_to_sync(delete_entity)()
            return Response({
                'deleted_count': count,
                'message': f'Deleted {count} index entries'
            })
        except Exception as e:
            logger.error(f"Error deleting entity indexes: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SearchViewSet(viewsets.ViewSet):
    """ViewSet for search operations"""
    permission_classes = [AllowAny]  # Search can be public
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = SearchService()
    
    @action(detail=False, methods=['get'])
    def query(self, request):
        """Perform a search query"""
        serializer = SearchQuerySerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            params = serializer.validated_data
            
            async def perform_search():
                async with self.service as svc:
                    return await svc.search(
                        query=params['q'],
                        entity_type=params.get('entity_type'),
                        language=params.get('language'),
                        limit=params.get('limit', 20),
                        offset=params.get('offset', 0)
                    )
            
            result = async_to_sync(perform_search)()
            return Response(result)
        except Exception as e:
            logger.error(f"Error performing search: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def by_keywords(self, request):
        """Search by specific keywords"""
        keywords = request.query_params.getlist('keywords')
        entity_type = request.query_params.get('entity_type')
        limit = int(request.query_params.get('limit', 20))
        
        if not keywords:
            return Response(
                {'error': 'Keywords parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            async def search_keywords():
                async with self.service as svc:
                    return await svc.search_by_keywords(keywords, entity_type, limit)
            
            results = async_to_sync(search_keywords)()
            return Response({
                'results': results,
                'total': len(results),
                'keywords': keywords
            })
        except Exception as e:
            logger.error(f"Error searching by keywords: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='entity/(?P<entity_type>[^/.]+)/(?P<entity_id>[^/.]+)')
    def by_entity(self, request, entity_type=None, entity_id=None):
        """Get search index for a specific entity"""
        try:
            async def get_entity():
                async with self.service as svc:
                    return await svc.get_by_entity(entity_type, entity_id)
            
            result = async_to_sync(get_entity)()
            if not result:
                return Response(
                    {'error': 'Entity not found in search index'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(result)
        except Exception as e:
            logger.error(f"Error getting entity: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get search statistics"""
        days = int(request.query_params.get('days', 7))
        
        try:
            async def get_stats():
                async with self.service as svc:
                    return await svc.get_search_stats(days)
            
            stats = async_to_sync(get_stats)()
            return Response(stats)
        except Exception as e:
            logger.error(f"Error getting search stats: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def popular_queries(self, request):
        """Get most popular search queries"""
        limit = int(request.query_params.get('limit', 10))
        
        try:
            async def get_popular():
                async with self.service as svc:
                    return await svc.get_popular_queries(limit)
            
            queries = async_to_sync(get_popular)()
            return Response({
                'queries': queries,
                'total': len(queries)
            })
        except Exception as e:
            logger.error(f"Error getting popular queries: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthCheckViewSet(viewsets.ViewSet):
    """Health check endpoint"""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def health(self, request):
        """Check service health"""
        try:
            service = SearchService()
            
            async def check_health():
                async with service as svc:
                    # Try a simple database query
                    count = await svc.db.searchindex.count()
                    return {
                        'status': 'healthy',
                        'service': 'search-service',
                        'indexed_items': count
                    }
            
            result = async_to_sync(check_health)()
            return Response(result)
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return Response(
                {
                    'status': 'unhealthy',
                    'service': 'search-service',
                    'error': str(e)
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )