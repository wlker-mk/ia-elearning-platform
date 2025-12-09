import pytest
from apps.courses.courses.services import CoursesService
import uuid

@pytest.fixture
async def courses_service():
    """Fixture pour le service"""
    service = CoursesService()
    await service.connect()
    yield service
    await service.disconnect()

@pytest.fixture
def sample_course_data():
    """Données de test pour un cours"""
    return {
        'title': 'Test Course Python',
        'subtitle': 'A comprehensive test course',
        'description': 'This is a detailed test course description',
        'categoryId': str(uuid.uuid4()),
        'language': 'ENGLISH',
        'difficulty': 'BEGINNER',
        'type': 'VIDEO_COURSE',
        'price': 99.99,
        'isFree': False,
        'estimatedDuration': 3600
    }

@pytest.mark.asyncio
class TestCoursesService:
    """Tests pour le service des cours"""
    
    async def test_create_course(self, courses_service, sample_course_data):
        """Test de création d'un cours"""
        instructor_id = str(uuid.uuid4())
        course = await courses_service.create_course(
            sample_course_data,
            instructor_id
        )
        
        assert course is not None
        assert course['title'] == sample_course_data['title']
        assert course['instructorId'] == instructor_id
        assert course['slug'] == 'test-course-python'
    
    async def test_create_course_unique_slug(self, courses_service, sample_course_data):
        """Test génération de slug unique"""
        instructor_id = str(uuid.uuid4())
        
        # Créer le premier cours
        course1 = await courses_service.create_course(
            sample_course_data,
            instructor_id
        )
        
        # Créer un deuxième cours avec le même titre
        course2 = await courses_service.create_course(
            sample_course_data,
            instructor_id
        )
        
        # Les slugs doivent être différents
        assert course1['slug'] != course2['slug']
        assert course2['slug'] == 'test-course-python-1'
    
    async def test_get_course_by_id(self, courses_service, sample_course_data):
        """Test récupération par ID"""
        instructor_id = str(uuid.uuid4())
        created_course = await courses_service.create_course(
            sample_course_data,
            instructor_id
        )
        
        course = await courses_service.get_course_by_id(created_course['id'])
        
        assert course is not None
        assert course['id'] == created_course['id']
    
    async def test_get_course_by_slug(self, courses_service, sample_course_data):
        """Test récupération par slug"""
        instructor_id = str(uuid.uuid4())
        await courses_service.create_course(sample_course_data, instructor_id)
        
        course = await courses_service.get_course_by_slug('test-course-python')
        
        assert course is not None
        assert course['slug'] == 'test-course-python'
    
    async def test_list_courses(self, courses_service, sample_course_data):
        """Test listage des cours"""
        instructor_id = str(uuid.uuid4())
        
        # Créer plusieurs cours
        for i in range(3):
            data = sample_course_data.copy()
            data['title'] = f'Test Course {i}'
            await courses_service.create_course(data, instructor_id)
        
        result = await courses_service.list_courses(skip=0, take=10)
        
        assert result['total'] >= 3
        assert len(result['courses']) >= 3
    
    async def test_list_courses_with_filters(self, courses_service, sample_course_data):
        """Test filtres de listage"""
        instructor_id = str(uuid.uuid4())
        
        # Créer des cours avec différentes difficultés
        for difficulty in ['BEGINNER', 'INTERMEDIATE']:
            data = sample_course_data.copy()
            data['difficulty'] = difficulty
            data['title'] = f'Course {difficulty}'
            await courses_service.create_course(data, instructor_id)
        
        # Filtrer par difficulté
        result = await courses_service.list_courses(
            filters={'difficulty': 'BEGINNER'}
        )
        
        assert all(
            course['difficulty'] == 'BEGINNER' 
            for course in result['courses']
        )
    
    async def test_update_course(self, courses_service, sample_course_data):
        """Test mise à jour"""
        instructor_id = str(uuid.uuid4())
        course = await courses_service.create_course(
            sample_course_data,
            instructor_id
        )
        
        updated = await courses_service.update_course(
            course['id'],
            {'title': 'Updated Title', 'price': 149.99}
        )
        
        assert updated['title'] == 'Updated Title'
        assert updated['price'] == 149.99
    
    async def test_delete_course(self, courses_service, sample_course_data):
        """Test suppression"""
        instructor_id = str(uuid.uuid4())
        course = await courses_service.create_course(
            sample_course_data,
            instructor_id
        )
        
        result = await courses_service.delete_course(course['id'])
        assert result is True
        
        # Vérifier que le cours n'existe plus
        deleted = await courses_service.get_course_by_id(course['id'])
        assert deleted is None
    
    async def test_publish_unpublish_course(self, courses_service, sample_course_data):
        """Test publication/dépublication"""
        instructor_id = str(uuid.uuid4())
        course = await courses_service.create_course(
            sample_course_data,
            instructor_id
        )
        
        # Publier
        published = await courses_service.publish_course(course['id'])
        assert published['publishedAt'] is not None
        
        # Dépublier
        unpublished = await courses_service.unpublish_course(course['id'])
        assert unpublished['publishedAt'] is None
    
    async def test_create_section(self, courses_service, sample_course_data):
        """Test création de section"""
        instructor_id = str(uuid.uuid4())
        course = await courses_service.create_course(
            sample_course_data,
            instructor_id
        )
        
        section_data = {
            'title': 'Introduction Section',
            'description': 'Getting started',
            'order': 1
        }
        
        section = await courses_service.create_section(
            course['id'],
            section_data
        )
        
        assert section is not None
        assert section['title'] == 'Introduction Section'
        assert section['courseId'] == course['id']
    
    async def test_create_lesson(self, courses_service, sample_course_data):
        """Test création de leçon"""
        instructor_id = str(uuid.uuid4())
        course = await courses_service.create_course(
            sample_course_data,
            instructor_id
        )
        
        section = await courses_service.create_section(
            course['id'],
            {'title': 'Section 1', 'order': 1}
        )
        
        lesson_data = {
            'title': 'Lesson 1',
            'description': 'First lesson',
            'order': 1,
            'videoUrl': 'https://example.com/video.mp4',
            'videoDuration': 600
        }
        
        lesson = await courses_service.create_lesson(
            section['id'],
            lesson_data
        )
        
        assert lesson is not None
        assert lesson['title'] == 'Lesson 1'
        assert lesson['sectionId'] == section['id']
    
    async def test_add_resource(self, courses_service, sample_course_data):
        """Test ajout de ressource"""
        instructor_id = str(uuid.uuid4())
        course = await courses_service.create_course(
            sample_course_data,
            instructor_id
        )
        
        section = await courses_service.create_section(
            course['id'],
            {'title': 'Section 1', 'order': 1}
        )
        
        lesson = await courses_service.create_lesson(
            section['id'],
            {'title': 'Lesson 1', 'order': 1}
        )
        
        resource_data = {
            'title': 'Course Slides',
            'type': 'PDF',
            'url': 'https://example.com/slides.pdf',
            'fileSize': 2048000
        }
        
        resource = await courses_service.add_resource(
            lesson['id'],
            resource_data
        )
        
        assert resource is not None
        assert resource['title'] == 'Course Slides'
        assert resource['lessonId'] == lesson['id']
    
    async def test_create_category(self, courses_service):
        """Test création de catégorie"""
        category_data = {
            'name': 'Web Development',
            'description': 'Learn web development'
        }
        
        category = await courses_service.create_category(category_data)
        
        assert category is not None
        assert category['name'] == 'Web Development'
        assert category['slug'] == 'web-development'
    
    async def test_create_tag(self, courses_service):
        """Test création de tag"""
        tag = await courses_service.create_tag('Python')
        
        assert tag is not None
        assert tag['name'] == 'Python'
        assert tag['slug'] == 'python'
    
    async def test_wishlist_operations(self, courses_service, sample_course_data):
        """Test opérations wishlist"""
        instructor_id = str(uuid.uuid4())
        student_id = str(uuid.uuid4())
        
        course = await courses_service.create_course(
            sample_course_data,
            instructor_id
        )
        
        # Ajouter
        item = await courses_service.add_to_wishlist(
            student_id,
            course['id']
        )
        
        assert item is not None
        assert item['studentId'] == student_id
        assert item['courseId'] == course['id']
        
        # Récupérer wishlist
        wishlist = await courses_service.get_wishlist(student_id)
        assert len(wishlist) >= 1
        
        # Retirer
        result = await courses_service.remove_from_wishlist(
            student_id,
            course['id']
        )
        assert result is True
    
    async def test_increment_enrollment_count(self, courses_service, sample_course_data):
        """Test incrémentation du compteur d'inscriptions"""
        instructor_id = str(uuid.uuid4())
        course = await courses_service.create_course(
            sample_course_data,
            instructor_id
        )
        
        initial_count = course['enrollmentCount']
        
        updated = await courses_service.increment_enrollment_count(course['id'])
        
        assert updated['enrollmentCount'] == initial_count + 1
    
    async def test_search_courses(self, courses_service, sample_course_data):
        """Test recherche de cours"""
        instructor_id = str(uuid.uuid4())
        
        # Créer un cours avec un titre spécifique
        data = sample_course_data.copy()
        data['title'] = 'Advanced Django Tutorial'
        await courses_service.create_course(data, instructor_id)
        
        # Rechercher
        result = await courses_service.list_courses(
            filters={'search': 'Django'}
        )
        
        assert result['total'] >= 1
        assert any('Django' in course['title'] for course in result['courses'])