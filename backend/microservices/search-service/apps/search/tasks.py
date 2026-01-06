from celery import shared_task
import logging
from asgiref.sync import async_to_sync
from .services import SearchService

logger = logging.getLogger(__name__)


@shared_task
def index_entity_task(entity_type: str, entity_id: str, title: str, content: str, 
                      keywords: list = None, language: str = 'en'):
    """
    Celery task to index an entity asynchronously
    """
    try:
        service = SearchService()
        
        async def index():
            async with service as svc:
                return await svc.create_index(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    title=title,
                    content=content,
                    keywords=keywords or [],
                    language=language
                )
        
        result = async_to_sync(index)()
        logger.info(f"Successfully indexed {entity_type}:{entity_id}")
        return result
    except Exception as e:
        logger.error(f"Error indexing entity: {str(e)}")
        raise


@shared_task
def update_entity_index_task(index_id: str, **kwargs):
    """
    Celery task to update an entity index asynchronously
    """
    try:
        service = SearchService()
        
        async def update():
            async with service as svc:
                return await svc.update_index(index_id, **kwargs)
        
        result = async_to_sync(update)()
        logger.info(f"Successfully updated index {index_id}")
        return result
    except Exception as e:
        logger.error(f"Error updating index: {str(e)}")
        raise


@shared_task
def delete_entity_index_task(entity_type: str, entity_id: str):
    """
    Celery task to delete entity indexes asynchronously
    """
    try:
        service = SearchService()
        
        async def delete():
            async with service as svc:
                return await svc.delete_by_entity(entity_type, entity_id)
        
        count = async_to_sync(delete)()
        logger.info(f"Successfully deleted {count} indexes for {entity_type}:{entity_id}")
        return count
    except Exception as e:
        logger.error(f"Error deleting entity indexes: {str(e)}")
        raise


@shared_task
def bulk_index_task(items: list):
    """
    Celery task to bulk index entities asynchronously
    """
    try:
        service = SearchService()
        
        async def bulk_index():
            async with service as svc:
                return await svc.bulk_index(items)
        
        result = async_to_sync(bulk_index)()
        logger.info(f"Successfully bulk indexed {result['success_count']} items")
        return result
    except Exception as e:
        logger.error(f"Error bulk indexing: {str(e)}")
        raise


@shared_task
def cleanup_old_tracking_task(days: int = 30):
    """
    Celery task to cleanup old search tracking records
    """
    try:
        from datetime import datetime, timedelta
        from prisma import Prisma
        
        async def cleanup():
            db = Prisma()
            await db.connect()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            result = await db.searchtracking.delete_many(
                where={
                    'createdAt': {'lt': cutoff_date}
                }
            )
            
            await db.disconnect()
            return result
        
        count = async_to_sync(cleanup)()
        logger.info(f"Cleaned up {count} old tracking records")
        return count
    except Exception as e:
        logger.error(f"Error cleaning up tracking: {str(e)}")
        raise


@shared_task
def reindex_entity_type_task(entity_type: str, entities_data: list):
    """
    Celery task to reindex all entities of a specific type
    Expects entities_data to be a list of dicts with: entity_id, title, content, keywords
    """
    try:
        service = SearchService()
        
        async def reindex():
            async with service as svc:
                # Delete existing indexes
                all_indexes = await svc.db.searchindex.find_many(
                    where={'entityType': entity_type}
                )
                
                for index in all_indexes:
                    await svc.delete_index(index.id)
                
                # Bulk create new indexes
                items = []
                for data in entities_data:
                    items.append({
                        'entity_type': entity_type,
                        'entity_id': data['entity_id'],
                        'title': data['title'],
                        'content': data['content'],
                        'keywords': data.get('keywords', []),
                        'language': data.get('language', 'en')
                    })
                
                return await svc.bulk_index(items)
        
        result = async_to_sync(reindex)()
        logger.info(f"Successfully reindexed {result['success_count']} items for {entity_type}")
        return result
    except Exception as e:
        logger.error(f"Error reindexing entity type: {str(e)}")
        raise


@shared_task
def generate_search_report_task(days: int = 7):
    """
    Celery task to generate a search analytics report
    """
    try:
        service = SearchService()
        
        async def generate_report():
            async with service as svc:
                stats = await svc.get_search_stats(days)
                popular = await svc.get_popular_queries(20)
                
                return {
                    'stats': stats,
                    'popular_queries': popular,
                    'period_days': days
                }
        
        report = async_to_sync(generate_report)()
        logger.info(f"Generated search report for {days} days")
        return report
    except Exception as e:
        logger.error(f"Error generating search report: {str(e)}")
        raise