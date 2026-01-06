import pytest
from apps.search.services import SearchService

@pytest.fixture
async def search_service():
    """Fixture to provide a connected SearchService"""
    service = SearchService()
    await service.connect()
    yield service
    await service.disconnect()


@pytest.mark.asyncio
async def test_create_index(search_service):
    """Test creating a search index"""
    result = await search_service.create_index(
        entity_type='course',
        entity_id='test-course-1',
        title='Test Course',
        content='This is a test course about Python programming',
        keywords=['python', 'programming', 'testing'],
        language='en'
    )
    
    assert result is not None
    assert result['entity_type'] == 'course'
    assert result['entity_id'] == 'test-course-1'
    assert result['title'] == 'Test Course'
    assert 'python' in result['keywords']


@pytest.mark.asyncio
async def test_update_index(search_service):
    """Test updating a search index"""
    # Create first
    created = await search_service.create_index(
        entity_type='course',
        entity_id='test-course-2',
        title='Original Title',
        content='Original content',
        keywords=['test'],
        language='en'
    )
    
    # Update
    updated = await search_service.update_index(
        index_id=created['id'],
        title='Updated Title',
        keywords=['test', 'updated']
    )
    
    assert updated is not None
    assert updated['title'] == 'Updated Title'
    assert 'updated' in updated['keywords']


@pytest.mark.asyncio
async def test_search(search_service):
    """Test searching indexed content"""
    # Create some test data
    await search_service.create_index(
        entity_type='course',
        entity_id='search-test-1',
        title='Python Programming',
        content='Learn Python from scratch',
        keywords=['python', 'beginner']
    )
    
    await search_service.create_index(
        entity_type='course',
        entity_id='search-test-2',
        title='JavaScript Basics',
        content='Introduction to JavaScript',
        keywords=['javascript', 'beginner']
    )
    
    # Search for Python
    results = await search_service.search(query='python', limit=10)
    
    assert results is not None
    assert results['total'] >= 1
    assert 'results' in results
    assert 'latency_ms' in results


@pytest.mark.asyncio
async def test_search_by_keywords(search_service):
    """Test searching by keywords"""
    await search_service.create_index(
        entity_type='course',
        entity_id='keyword-test-1',
        title='Advanced Python',
        content='Advanced Python concepts',
        keywords=['python', 'advanced', 'expert']
    )
    
    results = await search_service.search_by_keywords(
        keywords=['advanced', 'expert'],
        entity_type='course'
    )
    
    assert len(results) >= 1


@pytest.mark.asyncio
async def test_delete_index(search_service):
    """Test deleting a search index"""
    created = await search_service.create_index(
        entity_type='course',
        entity_id='delete-test-1',
        title='To Be Deleted',
        content='This will be deleted',
        keywords=['delete']
    )
    
    deleted = await search_service.delete_index(created['id'])
    assert deleted is True
    
    # Verify it's gone
    result = await search_service.get_by_entity('course', 'delete-test-1')
    assert result is None


@pytest.mark.asyncio
async def test_delete_by_entity(search_service):
    """Test deleting all indexes for an entity"""
    entity_id = 'bulk-delete-test'
    
    # Create multiple indexes for same entity
    await search_service.create_index(
        entity_type='course',
        entity_id=entity_id,
        title='Test 1',
        content='Content 1',
        keywords=[]
    )
    
    await search_service.create_index(
        entity_type='course',
        entity_id=entity_id,
        title='Test 2',
        content='Content 2',
        keywords=[]
    )
    
    count = await search_service.delete_by_entity('course', entity_id)
    assert count >= 2


@pytest.mark.asyncio
async def test_bulk_index(search_service):
    """Test bulk indexing"""
    items = [
        {
            'entity_type': 'course',
            'entity_id': 'bulk-1',
            'title': 'Bulk Course 1',
            'content': 'Content 1',
            'keywords': ['bulk']
        },
        {
            'entity_type': 'course',
            'entity_id': 'bulk-2',
            'title': 'Bulk Course 2',
            'content': 'Content 2',
            'keywords': ['bulk']
        },
    ]
    
    result = await search_service.bulk_index(items)
    
    assert result['success_count'] == 2
    assert result['error_count'] == 0
    assert len(result['created']) == 2


@pytest.mark.asyncio
async def test_get_search_stats(search_service):
    """Test getting search statistics"""
    # Perform some searches
    await search_service.search('test query 1')
    await search_service.search('test query 2')
    
    stats = await search_service.get_search_stats(days=7)
    
    assert 'total_searches' in stats
    assert 'avg_latency_ms' in stats
    assert 'total_indexed_items' in stats
    assert 'top_queries' in stats


@pytest.mark.asyncio
async def test_get_popular_queries(search_service):
    """Test getting popular queries"""
    # Perform searches
    await search_service.search('popular query')
    await search_service.search('popular query')
    await search_service.search('another query')
    
    popular = await search_service.get_popular_queries(limit=5)
    
    assert isinstance(popular, list)
    assert len(popular) > 0
    assert 'query' in popular[0]
    assert 'count' in popular[0]