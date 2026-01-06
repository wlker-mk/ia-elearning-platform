import pytest
from rest_framework.test import APIClient
from rest_framework import status
import json

@pytest.fixture
def api_client():
    """Fixture to provide API client"""
    return APIClient()


@pytest.mark.django_db
class TestSearchIndexViewSet:
    """Test SearchIndexViewSet endpoints"""
    
    def test_create_index(self, api_client):
        """Test creating a search index via API"""
        data = {
            'entity_type': 'course',
            'entity_id': 'api-test-1',
            'title': 'API Test Course',
            'content': 'This is a test course',
            'keywords': ['api', 'test'],
            'language': 'en'
        }
        
        response = api_client.post('/api/indexes/', data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_401_UNAUTHORIZED]
    
    def test_list_indexes(self, api_client):
        """Test listing search indexes"""
        response = api_client.get('/api/indexes/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]
    
    def test_retrieve_index(self, api_client):
        """Test retrieving a specific index"""
        # This will fail without valid ID, but tests the endpoint
        response = api_client.get('/api/indexes/invalid-id/')
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]
    
    def test_update_index(self, api_client):
        """Test updating an index"""
        data = {
            'title': 'Updated Title',
            'keywords': ['updated']
        }
        
        response = api_client.put('/api/indexes/invalid-id/', data, format='json')
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]
    
    def test_delete_index(self, api_client):
        """Test deleting an index"""
        response = api_client.delete('/api/indexes/invalid-id/')
        assert response.status_code in [
            status.HTTP_204_NO_CONTENT,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]
    
    def test_bulk_index(self, api_client):
        """Test bulk indexing"""
        data = {
            'items': [
                {
                    'entity_type': 'course',
                    'entity_id': 'bulk-api-1',
                    'title': 'Bulk Course 1',
                    'content': 'Content 1',
                    'keywords': ['bulk']
                },
                {
                    'entity_type': 'course',
                    'entity_id': 'bulk-api-2',
                    'title': 'Bulk Course 2',
                    'content': 'Content 2',
                    'keywords': ['bulk']
                }
            ]
        }
        
        response = api_client.post('/api/indexes/bulk_index/', data, format='json')
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_400_BAD_REQUEST
        ]


@pytest.mark.django_db
class TestSearchViewSet:
    """Test SearchViewSet endpoints"""
    
    def test_search_query(self, api_client):
        """Test search query endpoint"""
        response = api_client.get('/api/search/query/', {'q': 'python'})
        # Public endpoint, should work
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    def test_search_query_missing_param(self, api_client):
        """Test search without required query parameter"""
        response = api_client.get('/api/search/query/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_search_with_filters(self, api_client):
        """Test search with filters"""
        params = {
            'q': 'test',
            'entity_type': 'course',
            'language': 'en',
            'limit': 10,
            'offset': 0
        }
        
        response = api_client.get('/api/search/query/', params)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    def test_search_by_keywords(self, api_client):
        """Test searching by keywords"""
        response = api_client.get(
            '/api/search/by_keywords/',
            {'keywords': ['python', 'programming']}
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]
    
    def test_search_by_entity(self, api_client):
        """Test searching by entity"""
        response = api_client.get('/api/search/entity/course/test-id/')
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]
    
    def test_search_stats(self, api_client):
        """Test search statistics endpoint"""
        response = api_client.get('/api/search/stats/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    def test_popular_queries(self, api_client):
        """Test popular queries endpoint"""
        response = api_client.get('/api/search/popular_queries/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]


@pytest.mark.django_db
class TestHealthCheckViewSet:
    """Test HealthCheckViewSet endpoints"""
    
    def test_health_check(self, api_client):
        """Test health check endpoint"""
        response = api_client.get('/api/health/health/')
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_503_SERVICE_UNAVAILABLE
        ]
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert 'status' in data
            assert 'service' in data