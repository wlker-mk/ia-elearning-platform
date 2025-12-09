import pytest
from apps.courses.lessons.services import LessonsService
import uuid

@pytest.fixture
async def lessons_service():
    """Fixture pour le service lessons"""
    service = LessonsService()
    await service.connect()
    yield service
    await service.disconnect()

@pytest.fixture
async def sample_course_and_section(courses_service):
    """Créer un cours et une section de test"""
    course_data = {
        'title': 'Test Course',
        'description': 'Test description',
        'categoryId': str(uuid.uuid4()),
        'difficulty': 'BEGINNER',
        'type': 'VIDEO_COURSE',
        'price': 99.99,
        'estimatedDuration': 3600
    }
    
    instructor_id = str(uuid.uuid4())
    course = await courses_service.create_course(course_data, instructor_id)
    
    section = await courses_service.create_section(
        course['id'],
        {'title': 'Test Section', 'order': 1}
    )
    
    return {'course': course, 'section': section}

@pytest.mark.asyncio
class TestLessonsService:
    """Tests pour le service des leçons"""
    
    async def test_create_lesson(self, lessons_service, sample_course_and_section):
        """Test création de leçon"""
        section = sample_course_and_section['section']
        
        lesson_data = {
            'sectionId': section['id'],
            'title': 'Test Lesson',
            'description': 'Test lesson description',
            'order': 1,
            'videoUrl': 'https://example.com/video.mp4',
            'videoDuration': 600
        }
        
        lesson = await lessons_service.create_lesson(lesson_data)
        
        assert lesson is not None
        assert lesson['title'] == 'Test Lesson'
        assert lesson['sectionId'] == section['id']
    
    async def test_get_lesson_by_id(self, lessons_service, sample_course_and_section):
        """Test récupération par ID"""
        section = sample_course_and_section['section']
        
        created = await lessons_service.create_lesson({
            'sectionId': section['id'],
            'title': 'Test Lesson',
            'order': 1
        })
        
        lesson = await lessons_service.get_lesson_by_id(created['id'])
        
        assert lesson is not None
        assert lesson['id'] == created['id']
    
    async def test_list_lessons_by_section(
        self, 
        lessons_service, 
        sample_course_and_section
    ):
        """Test listage par section"""
        section = sample_course_and_section['section']
        
        # Créer plusieurs leçons
        for i in range(3):
            await lessons_service.create_lesson({
                'sectionId': section['id'],
                'title': f'Lesson {i}',
                'order': i + 1
            })
        
        lessons = await lessons_service.list_lessons_by_section(section['id'])
        
        assert len(lessons) == 3
        # Vérifier l'ordre
        assert lessons[0]['order'] < lessons[1]['order'] < lessons[2]['order']
    
    async def test_update_lesson(self, lessons_service, sample_course_and_section):
        """Test mise à jour"""
        section = sample_course_and_section['section']
        
        lesson = await lessons_service.create_lesson({
            'sectionId': section['id'],
            'title': 'Original Title',
            'order': 1
        })
        
        updated = await lessons_service.update_lesson(
            lesson['id'],
            {'title': 'Updated Title', 'videoDuration': 900}
        )
        
        assert updated['title'] == 'Updated Title'
        assert updated['videoDuration'] == 900
    
    async def test_delete_lesson(self, lessons_service, sample_course_and_section):
        """Test suppression"""
        section = sample_course_and_section['section']
        
        lesson = await lessons_service.create_lesson({
            'sectionId': section['id'],
            'title': 'To Delete',
            'order': 1
        })
        
        result = await lessons_service.delete_lesson(lesson['id'])
        assert result is True
        
        deleted = await lessons_service.get_lesson_by_id(lesson['id'])
        assert deleted is None
    
    async def test_reorder_lessons(self, lessons_service, sample_course_and_section):
        """Test réorganisation"""
        section = sample_course_and_section['section']
        
        # Créer 3 leçons
        lessons = []
        for i in range(3):
            lesson = await lessons_service.create_lesson({
                'sectionId': section['id'],
                'title': f'Lesson {i}',
                'order': i + 1
            })
            lessons.append(lesson)
        
        # Inverser l'ordre
        new_order = [
            {'id': lessons[0]['id'], 'order': 3},
            {'id': lessons[1]['id'], 'order': 2},
            {'id': lessons[2]['id'], 'order': 1}
        ]
        
        result = await lessons_service.reorder_lessons(section['id'], new_order)
        assert result is True
        
        # Vérifier le nouvel ordre
        reordered = await lessons_service.list_lessons_by_section(section['id'])
        assert reordered[0]['id'] == lessons[2]['id']
        assert reordered[2]['id'] == lessons[0]['id']
    
    async def test_duplicate_lesson(self, lessons_service, sample_course_and_section):
        """Test duplication"""
        section = sample_course_and_section['section']
        
        original = await lessons_service.create_lesson({
            'sectionId': section['id'],
            'title': 'Original Lesson',
            'description': 'Original description',
            'order': 1,
            'videoDuration': 600
        })
        
        duplicate = await lessons_service.duplicate_lesson(original['id'])
        
        assert duplicate is not None
        assert duplicate['id'] != original['id']
        assert 'Copy' in duplicate['title']
        assert duplicate['description'] == original['description']
    
    async def test_add_resource(self, lessons_service, sample_course_and_section):
        """Test ajout de ressource"""
        section = sample_course_and_section['section']
        
        lesson = await lessons_service.create_lesson({
            'sectionId': section['id'],
            'title': 'Test Lesson',
            'order': 1
        })
        
        resource_data = {
            'lessonId': lesson['id'],
            'title': 'Course Slides',
            'type': 'PDF',
            'url': 'https://example.com/slides.pdf',
            'fileSize': 2048000
        }
        
        resource = await lessons_service.add_resource(resource_data)
        
        assert resource is not None
        assert resource['title'] == 'Course Slides'
        assert resource['lessonId'] == lesson['id']
    
    async def test_list_resources_by_lesson(
        self, 
        lessons_service, 
        sample_course_and_section
    ):
        """Test listage des ressources"""
        section = sample_course_and_section['section']
        
        lesson = await lessons_service.create_lesson({
            'sectionId': section['id'],
            'title': 'Test Lesson',
            'order': 1
        })
        
        # Ajouter plusieurs ressources
        for i in range(3):
            await lessons_service.add_resource({
                'lessonId': lesson['id'],
                'title': f'Resource {i}',
                'type': 'PDF',
                'url': f'https://example.com/resource{i}.pdf'
            })
        
        resources = await lessons_service.list_resources_by_lesson(lesson['id'])
        
        assert len(resources) == 3
    
    async def test_track_resource_download(
        self, 
        lessons_service, 
        sample_course_and_section
    ):
        """Test tracking de téléchargement"""
        section = sample_course_and_section['section']
        
        lesson = await lessons_service.create_lesson({
            'sectionId': section['id'],
            'title': 'Test Lesson',
            'order': 1
        })
        
        resource = await lessons_service.add_resource({
            'lessonId': lesson['id'],
            'title': 'Test Resource',
            'type': 'PDF',
            'url': 'https://example.com/test.pdf'
        })
        
        initial_count = resource['downloadCount']
        
        updated = await lessons_service.track_resource_download(resource['id'])
        
        assert updated['downloadCount'] == initial_count + 1
    
    async def test_get_next_lesson(self, lessons_service, sample_course_and_section):
        """Test récupération de la leçon suivante"""
        section = sample_course_and_section['section']
        
        # Créer 3 leçons
        lesson1 = await lessons_service.create_lesson({
            'sectionId': section['id'],
            'title': 'Lesson 1',
            'order': 1
        })
        
        lesson2 = await lessons_service.create_lesson({
            'sectionId': section['id'],
            'title': 'Lesson 2',
            'order': 2
        })
        
        # Récupérer la leçon suivante
        next_lesson = await lessons_service.get_next_lesson(lesson1['id'])
        
        assert next_lesson is not None
        assert next_lesson['id'] == lesson2['id']
    
    async def test_get_previous_lesson(
        self, 
        lessons_service, 
        sample_course_and_section
    ):
        """Test récupération de la leçon précédente"""
        section = sample_course_and_section['section']
        
        # Créer 2 leçons
        lesson1 = await lessons_service.create_lesson({
            'sectionId': section['id'],
            'title': 'Lesson 1',
            'order': 1
        })
        
        lesson2 = await lessons_service.create_lesson({
            'sectionId': section['id'],
            'title': 'Lesson 2',
            'order': 2
        })
        
        # Récupérer la leçon précédente
        prev_lesson = await lessons_service.get_previous_lesson(lesson2['id'])
        
        assert prev_lesson is not None
        assert prev_lesson['id'] == lesson1['id']
    
    async def test_validate_lesson_access_free(
        self, 
        lessons_service, 
        sample_course_and_section
    ):
        """Test validation d'accès pour leçon gratuite"""
        section = sample_course_and_section['section']
        
        lesson = await lessons_service.create_lesson({
            'sectionId': section['id'],
            'title': 'Free Lesson',
            'order': 1,
            'isFree': True
        })
        
        result = await lessons_service.validate_lesson_access(
            lesson['id'],
            str(uuid.uuid4()),
            False  # Pas d'inscription
        )
        
        assert result['hasAccess'] is True
        assert result['reason'] == 'Free lesson'
    
    async def test_validate_lesson_access_enrolled(
        self, 
        lessons_service, 
        sample_course_and_section
    ):
        """Test validation d'accès pour utilisateur inscrit"""
        section = sample_course_and_section['section']
        
        lesson = await lessons_service.create_lesson({
            'sectionId': section['id'],
            'title': 'Paid Lesson',
            'order': 1,
            'isFree': False
        })
        
        result = await lessons_service.validate_lesson_access(
            lesson['id'],
            str(uuid.uuid4()),
            True  # Inscrit
        )
        
        assert result['hasAccess'] is True
        assert result['reason'] == 'Enrolled'
    
    async def test_validate_lesson_access_denied(
        self, 
        lessons_service, 
        sample_course_and_section
    ):
        """Test validation d'accès refusé"""
        section = sample_course_and_section['section']
        
        lesson = await lessons_service.create_lesson({
            'sectionId': section['id'],
            'title': 'Paid Lesson',
            'order': 1,
            'isFree': False
        })
        
        result = await lessons_service.validate_lesson_access(
            lesson['id'],
            str(uuid.uuid4()),
            False  # Pas inscrit
        )
        
        assert result['hasAccess'] is False
        assert result['reason'] == 'Enrollment required'