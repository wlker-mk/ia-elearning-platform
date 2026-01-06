from typing import List, Optional, Dict, Any
from prisma import Prisma
from django.core.cache import cache
import logging
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self):
        self.db = Prisma()
        self._connected = False
    
    async def connect(self):
        """Connect to database"""
        if not self._connected:
            await self.db.connect()
            self._connected = True
            logger.info("SearchService connected to database")
    
    async def disconnect(self):
        """Disconnect from database"""
        if self._connected:
            await self.db.disconnect()
            self._connected = False
            logger.info("SearchService disconnected from database")
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    # ==================== INDEXING METHODS ====================
    
    async def create_index(
        self,
        entity_type: str,
        entity_id: str,
        title: str,
        content: str,
        keywords: List[str] = None,
        language: str = 'en'
    ) -> Dict[str, Any]:
        """Create a new search index entry"""
        try:
            index = await self.db.searchindex.create(
                data={
                    'entityType': entity_type,
                    'entityId': entity_id,
                    'title': title,
                    'content': content,
                    'keywords': keywords or [],
                    'language': language
                }
            )
            
            # Invalidate cache
            self._invalidate_cache(entity_type)
            
            logger.info(f"Created index for {entity_type}:{entity_id}")
            return self._format_index(index)
        except Exception as e:
            logger.error(f"Error creating index: {str(e)}")
            raise
    
    async def update_index(
        self,
        index_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update an existing search index entry"""
        try:
            data = {}
            if title is not None:
                data['title'] = title
            if content is not None:
                data['content'] = content
            if keywords is not None:
                data['keywords'] = keywords
            if language is not None:
                data['language'] = language
            
            index = await self.db.searchindex.update(
                where={'id': index_id},
                data=data
            )
            
            if index:
                self._invalidate_cache(index.entityType)
                logger.info(f"Updated index {index_id}")
            
            return self._format_index(index) if index else None
        except Exception as e:
            logger.error(f"Error updating index: {str(e)}")
            raise
    
    async def delete_index(self, index_id: str) -> bool:
        """Delete a search index entry"""
        try:
            index = await self.db.searchindex.delete(
                where={'id': index_id}
            )
            
            if index:
                self._invalidate_cache(index.entityType)
                logger.info(f"Deleted index {index_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting index: {str(e)}")
            raise
    
    async def delete_by_entity(self, entity_type: str, entity_id: str) -> int:
        """Delete all index entries for a specific entity"""
        try:
            result = await self.db.searchindex.delete_many(
                where={
                    'entityType': entity_type,
                    'entityId': entity_id
                }
            )
            
            self._invalidate_cache(entity_type)
            logger.info(f"Deleted {result} indexes for {entity_type}:{entity_id}")
            return result
        except Exception as e:
            logger.error(f"Error deleting entity indexes: {str(e)}")
            raise
    
    async def bulk_index(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk create search index entries"""
        try:
            created_items = []
            errors = []
            
            for item in items:
                try:
                    index = await self.db.searchindex.create(
                        data={
                            'entityType': item['entity_type'],
                            'entityId': item['entity_id'],
                            'title': item['title'],
                            'content': item['content'],
                            'keywords': item.get('keywords', []),
                            'language': item.get('language', 'en')
                        }
                    )
                    created_items.append(self._format_index(index))
                except Exception as e:
                    errors.append({
                        'item': item,
                        'error': str(e)
                    })
            
            # Invalidate cache for all entity types
            entity_types = set(item['entity_type'] for item in items)
            for entity_type in entity_types:
                self._invalidate_cache(entity_type)
            
            logger.info(f"Bulk indexed {len(created_items)} items with {len(errors)} errors")
            
            return {
                'created': created_items,
                'errors': errors,
                'total': len(items),
                'success_count': len(created_items),
                'error_count': len(errors)
            }
        except Exception as e:
            logger.error(f"Error in bulk indexing: {str(e)}")
            raise

    # ==================== SEARCH METHODS ====================
    
    async def search(
        self,
        query: str,
        entity_type: Optional[str] = None,
        language: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Search indexed content"""
        start_time = time.time()
        
        try:
            # Build where clause
            where = {}
            or_conditions = []
            
            # Full-text search simulation (PostgreSQL doesn't have native full-text in Prisma)
            # We search in title, content, and keywords
            search_term = query.lower()
            
            if entity_type:
                where['entityType'] = entity_type
            
            if language:
                where['language'] = language
            
            # Get all matching records (we'll filter in Python)
            all_records = await self.db.searchindex.find_many(
                where=where,
                order={'createdAt': 'desc'}
            )
            
            # Filter by search term
            results = []
            for record in all_records:
                if self._matches_search(record, search_term):
                    results.append(record)
            
            total = len(results)
            
            # Apply pagination
            paginated_results = results[offset:offset + limit]
            
            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Track search
            await self._track_search(query, total, latency_ms)
            
            logger.info(f"Search '{query}' returned {total} results in {latency_ms}ms")
            
            return {
                'results': [self._format_index(r) for r in paginated_results],
                'total': total,
                'query': query,
                'limit': limit,
                'offset': offset,
                'latency_ms': latency_ms
            }
        except Exception as e:
            logger.error(f"Error searching: {str(e)}")
            raise
    
    async def search_by_keywords(
        self,
        keywords: List[str],
        entity_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search by specific keywords"""
        try:
            where = {}
            if entity_type:
                where['entityType'] = entity_type
            
            all_records = await self.db.searchindex.find_many(
                where=where,
                take=limit * 2  # Get more to filter
            )
            
            # Filter by keywords
            results = []
            for record in all_records:
                if any(kw.lower() in [k.lower() for k in record.keywords] for kw in keywords):
                    results.append(self._format_index(record))
                    if len(results) >= limit:
                        break
            
            logger.info(f"Keyword search returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Error in keyword search: {str(e)}")
            raise
    
    async def get_by_entity(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get index entry for a specific entity"""
        try:
            index = await self.db.searchindex.find_first(
                where={
                    'entityType': entity_type,
                    'entityId': entity_id
                }
            )
            return self._format_index(index) if index else None
        except Exception as e:
            logger.error(f"Error getting entity index: {str(e)}")
            raise
    
    async def get_all_by_type(
        self,
        entity_type: str,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get all indexed items of a specific type"""
        try:
            # Try cache first
            cache_key = f"search:type:{entity_type}:{limit}:{offset}"
            cached = cache.get(cache_key)
            if cached:
                return cached
            
            records = await self.db.searchindex.find_many(
                where={'entityType': entity_type},
                take=limit,
                skip=offset,
                order={'createdAt': 'desc'}
            )
            
            total = await self.db.searchindex.count(
                where={'entityType': entity_type}
            )
            
            result = {
                'results': [self._format_index(r) for r in records],
                'total': total,
                'limit': limit,
                'offset': offset
            }
            
            # Cache for 5 minutes
            cache.set(cache_key, result, 300)
            
            return result
        except Exception as e:
            logger.error(f"Error getting items by type: {str(e)}")
            raise

    # ==================== TRACKING & STATS METHODS ====================
    
    async def _track_search(self, query: str, result_count: int, latency_ms: int):
        """Track search query for analytics"""
        try:
            await self.db.searchtracking.create(
                data={
                    'query': query,
                    'resultCount': result_count,
                    'latencyMs': latency_ms
                }
            )
        except Exception as e:
            logger.warning(f"Error tracking search: {str(e)}")
    
    async def get_search_stats(
        self,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get search statistics"""
        try:
            since = datetime.now() - timedelta(days=days)
            
            # Get all tracking records
            tracking = await self.db.searchtracking.find_many(
                where={
                    'createdAt': {'gte': since}
                }
            )
            
            if not tracking:
                return {
                    'total_searches': 0,
                    'avg_latency_ms': 0,
                    'total_indexed_items': 0,
                    'top_queries': []
                }
            
            # Calculate stats
            total_searches = len(tracking)
            avg_latency = sum(t.latencyMs for t in tracking) / total_searches
            
            # Count indexed items
            total_indexed = await self.db.searchindex.count()
            
            # Top queries
            query_counts = {}
            for t in tracking:
                query_counts[t.query] = query_counts.get(t.query, 0) + 1
            
            top_queries = sorted(
                [{'query': q, 'count': c} for q, c in query_counts.items()],
                key=lambda x: x['count'],
                reverse=True
            )[:10]
            
            return {
                'total_searches': total_searches,
                'avg_latency_ms': round(avg_latency, 2),
                'total_indexed_items': total_indexed,
                'top_queries': top_queries
            }
        except Exception as e:
            logger.error(f"Error getting search stats: {str(e)}")
            raise
    
    async def get_popular_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular search queries"""
        try:
            # Get recent tracking
            tracking = await self.db.searchtracking.find_many(
                order={'createdAt': 'desc'},
                take=1000
            )
            
            # Count queries
            query_counts = {}
            for t in tracking:
                query_counts[t.query] = query_counts.get(t.query, 0) + 1
            
            popular = sorted(
                [{'query': q, 'count': c} for q, c in query_counts.items()],
                key=lambda x: x['count'],
                reverse=True
            )[:limit]
            
            return popular
        except Exception as e:
            logger.error(f"Error getting popular queries: {str(e)}")
            raise

    # ==================== HELPER METHODS ====================
    
    def _matches_search(self, record, search_term: str) -> bool:
        """Check if record matches search term"""
        search_fields = [
            record.title.lower(),
            record.content.lower(),
            ' '.join(record.keywords).lower()
        ]
        
        return any(search_term in field for field in search_fields)
    
    def _format_index(self, index) -> Dict[str, Any]:
        """Format index record for API response"""
        if not index:
            return None
        
        return {
            'id': index.id,
            'entity_type': index.entityType,
            'entity_id': index.entityId,
            'title': index.title,
            'content': index.content,
            'keywords': index.keywords,
            'language': index.language,
            'created_at': index.createdAt.isoformat(),
            'updated_at': index.updatedAt.isoformat()
        }
    
    def _invalidate_cache(self, entity_type: str):
        """Invalidate cache for entity type"""
        pattern = f"search:type:{entity_type}:*"
        cache.delete_pattern(pattern)