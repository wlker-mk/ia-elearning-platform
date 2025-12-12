import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime, timedelta
from prisma import Prisma


@pytest.fixture
def db():
    """Prisma database fixture"""
    db = Prisma()
    db.connect()
    yield db
    db.disconnect()


@pytest.fixture
def api_client():
    """API client fixture"""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client):
    """Authenticated API client"""
    # Mock JWT token
    api_client.credentials(HTTP_AUTHORIZATION='Bearer test-token')
    return api_client


class EnrollmentTests(TestCase):
    """Tests for enrollment endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer test-token')
        self.db = Prisma()
        self.db.connect()
    
    def tearDown(self):
        self.db.disconnect()
    
    def test_create_enrollment(self):
        """Test creating a new enrollment"""
        data = {
            'courseId': 'test-course-id',
            'purchasePrice': 99.99,
            'paymentId': 'test-payment-id'
        }
        
        response = self.client.post('/api/v1/enrollments/', data, format='json')
        
        # Should return 201 Created or 200 OK depending on implementation
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        self.assertTrue(response.data['success'])
    
    def test_list_enrollments(self):
        """Test listing enrollments"""
        response = self.client.get('/api/v1/enrollments/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
    
    def test_get_enrollment_detail(self):
        """Test getting enrollment details"""
        # Create a test enrollment first
        enrollment = self.db.enrollment.create(
            data={
                'studentId': 'test-student',
                'courseId': 'test-course',
                'status': 'ACTIVE'
            }
        )
        
        response = self.client.get(f'/api/v1/enrollments/{enrollment.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['id'], enrollment.id)


class ProgressTests(TestCase):
    """Tests for progress endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer test-token')
        self.db = Prisma()
        self.db.connect()
        
        # Create test enrollment
        self.enrollment = self.db.enrollment.create(
            data={
                'studentId': 'test-student',
                'courseId': 'test-course',
                'status': 'ACTIVE'
            }
        )
    
    def tearDown(self):
        self.db.disconnect()
    
    def test_create_progress(self):
        """Test creating progress record"""
        data = {
            'lessonId': 'test-lesson',
            'courseId': 'test-course',
            'percentage': 50.0,
            'timeSpent': 1800
        }
        
        response = self.client.post('/api/v1/enrollments/progress/', data, format='json')
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        self.assertTrue(response.data['success'])
    
    def test_get_course_progress(self):
        """Test getting course progress"""
        response = self.client.get('/api/v1/enrollments/progress/course/test-course/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])


class NoteTests(TestCase):
    """Tests for note endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer test-token')
        self.db = Prisma()
        self.db.connect()
        
        # Create test enrollment
        self.enrollment = self.db.enrollment.create(
            data={
                'studentId': 'test-student',
                'courseId': 'test-course',
                'status': 'ACTIVE'
            }
        )
    
    def tearDown(self):
        self.db.disconnect()
    
    def test_create_note(self):
        """Test creating a note"""
        data = {
            'courseId': 'test-course',
            'lessonId': 'test-lesson',
            'type': 'TEXT',
            'content': 'Test note content'
        }
        
        response = self.client.post('/api/v1/enrollments/notes/', data, format='json')
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        self.assertTrue(response.data['success'])
    
    def test_list_notes(self):
        """Test listing notes"""
        response = self.client.get('/api/v1/enrollments/notes/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])


class BookmarkTests(TestCase):
    """Tests for bookmark endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer test-token')
        self.db = Prisma()
        self.db.connect()
        
        # Create test enrollment
        self.enrollment = self.db.enrollment.create(
            data={
                'studentId': 'test-student',
                'courseId': 'test-course',
                'status': 'ACTIVE'
            }
        )
    
    def tearDown(self):
        self.db.disconnect()
    
    def test_create_bookmark(self):
        """Test creating a bookmark"""
        data = {
            'courseId': 'test-course',
            'lessonId': 'test-lesson',
            'type': 'LESSON',
            'title': 'Test Bookmark'
        }
        
        response = self.client.post('/api/v1/enrollments/notes/bookmarks/', data, format='json')
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        self.assertTrue(response.data['success'])


# Integration Tests
@pytest.mark.django_db
class EnrollmentFlowTest:
    """Test complete enrollment flow"""
    
    def test_complete_enrollment_flow(self, authenticated_client, db):
        """Test complete enrollment workflow"""
        
        # 1. Create enrollment
        enrollment_data = {
            'courseId': 'flow-test-course',
            'purchasePrice': 149.99
        }
        
        response = authenticated_client.post(
            '/api/v1/enrollments/',
            enrollment_data,
            format='json'
        )
        
        assert response.status_code in [200, 201]
        enrollment_id = response.data['data']['id']
        
        # 2. Update progress
        progress_data = {
            'lessonId': 'lesson-1',
            'courseId': 'flow-test-course',
            'percentage': 100,
            'isCompleted': True
        }
        
        response = authenticated_client.post(
            '/api/v1/enrollments/progress/',
            progress_data,
            format='json'
        )
        
        assert response.status_code in [200, 201]
        
        # 3. Add note
        note_data = {
            'courseId': 'flow-test-course',
            'lessonId': 'lesson-1',
            'type': 'TEXT',
            'content': 'Important concept!'
        }
        
        response = authenticated_client.post(
            '/api/v1/enrollments/notes/',
            note_data,
            format='json'
        )
        
        
        assert response.status_code in [200, 201]
        
        # 4. Check enrollment details
        response = authenticated_client.get(
            f'/api/v1/enrollments/{enrollment_id}/'
        )
        
        assert response.status_code == 200
        assert response.data['success']