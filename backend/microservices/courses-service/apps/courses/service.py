from typing import List, Optional, Dict, Any
from prisma import Prisma
from django.utils.text import slugify
from datetime import datetime

class CoursesService:
    def __init__(self):
        self.db = Prisma()
    
    async def connect(self):
        await self.db.connect()
    
    async def disconnect(self):
        await self.db.disconnect()
    
    # ========== COURSES ==========
    
    async def create_course(self, data: Dict[str, Any], instructor_id: str) -> Dict:
        """Créer un nouveau cours"""
        slug = slugify(data['title'])
        base_slug = slug
        counter = 1
        
        # Générer un slug unique
        while await self.db.course.find_first(where={'slug': slug}):
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        course_data = {
            'slug': slug,
            'title': data['title'],
            'subtitle': data.get('subtitle'),
            'description': data['description'],
            'instructorId': instructor_id,
            'categoryId': data['categoryId'],
            'language': data.get('language', 'ENGLISH'),
            'difficulty': data['difficulty'],
            'type': data['type'],
            'price': data['price'],
            'isFree': data.get('isFree', False),
            'thumbnailUrl': data.get('thumbnailUrl'),
            'estimatedDuration': data['estimatedDuration'],
        }
        
        course = await self.db.course.create(data=course_data)
        
        # Ajouter les tags si présents
        if 'tagIds' in data:
            for tag_id in data['tagIds']:
                await self.db.coursetag.create(data={
                    'courseId': course.id,
                    'tagId': tag_id
                })
                # Incrémenter usage count
                await self.db.tag.update(
                    where={'id': tag_id},
                    data={'usageCount': {'increment': 1}}
                )
        
        return await self.get_course_by_id(course.id)
    
    async def get_course_by_id(self, course_id: str) -> Optional[Dict]:
        """Récupérer un cours avec ses relations"""
        course = await self.db.course.find_unique(
            where={'id': course_id},
            include={
                'sections': {
                    'include': {
                        'lessons': {
                            'include': {'resources': True},
                            'order_by': {'order': 'asc'}
                        }
                    },
                    'order_by': {'order': 'asc'}
                },
                'tags': True
            }
        )
        return course
    
    async def get_course_by_slug(self, slug: str) -> Optional[Dict]:
        """Récupérer un cours par slug"""
        course = await self.db.course.find_unique(
            where={'slug': slug},
            include={
                'sections': {
                    'include': {
                        'lessons': {
                            'include': {'resources': True},
                            'order_by': {'order': 'asc'}
                        }
                    },
                    'order_by': {'order': 'asc'}
                }
            }
        )
        return course
    
    async def list_courses(
        self, 
        skip: int = 0, 
        take: int = 20,
        filters: Optional[Dict] = None
    ) -> Dict:
        """Lister les cours avec filtres"""
        where = {}
        
        if filters:
            if 'instructorId' in filters:
                where['instructorId'] = filters['instructorId']
            if 'categoryId' in filters:
                where['categoryId'] = filters['categoryId']
            if 'difficulty' in filters:
                where['difficulty'] = filters['difficulty']
            if 'isFree' in filters:
                where['isFree'] = filters['isFree']
            if 'search' in filters:
                where['OR'] = [
                    {'title': {'contains': filters['search'], 'mode': 'insensitive'}},
                    {'description': {'contains': filters['search'], 'mode': 'insensitive'}}
                ]
            if 'published' in filters:
                if filters['published']:
                    where['publishedAt'] = {'not': None}
                else:
                    where['publishedAt'] = None
        
        courses = await self.db.course.find_many(
            where=where,
            skip=skip,
            take=take,
            order_by={'createdAt': 'desc'}
        )
        
        total = await self.db.course.count(where=where)
        
        return {
            'courses': courses,
            'total': total,
            'skip': skip,
            'take': take
        }
    
    async def update_course(self, course_id: str, data: Dict[str, Any]) -> Optional[Dict]:
        """Mettre à jour un cours"""
        update_data = {}
        
        allowed_fields = [
            'title', 'subtitle', 'description', 'categoryId', 
            'language', 'difficulty', 'type', 'price', 'isFree',
            'thumbnailUrl', 'estimatedDuration'
        ]
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if 'title' in update_data:
            slug = slugify(update_data['title'])
            update_data['slug'] = slug
        
        course = await self.db.course.update(
            where={'id': course_id},
            data=update_data
        )
        
        return await self.get_course_by_id(course.id)
    
    async def delete_course(self, course_id: str) -> bool:
        """Supprimer un cours"""
        await self.db.course.delete(where={'id': course_id})
        return True
    
    async def publish_course(self, course_id: str) -> Dict:
        """Publier un cours"""
        course = await self.db.course.update(
            where={'id': course_id},
            data={'publishedAt': datetime.utcnow()}
        )
        return course
    
    async def unpublish_course(self, course_id: str) -> Dict:
        """Dépublier un cours"""
        course = await self.db.course.update(
            where={'id': course_id},
            data={'publishedAt': None}
        )
        return course
    
    # ========== SECTIONS ==========
    
    async def create_section(self, course_id: str, data: Dict[str, Any]) -> Dict:
        """Créer une section"""
        section = await self.db.section.create(data={
            'courseId': course_id,
            'title': data['title'],
            'description': data.get('description'),
            'order': data['order']
        })
        return section
    
    async def update_section(self, section_id: str, data: Dict[str, Any]) -> Dict:
        """Mettre à jour une section"""
        section = await self.db.section.update(
            where={'id': section_id},
            data=data
        )
        return section
    
    async def delete_section(self, section_id: str) -> bool:
        """Supprimer une section"""
        await self.db.section.delete(where={'id': section_id})
        return True
    
    async def reorder_sections(self, course_id: str, section_orders: List[Dict]) -> bool:
        """Réorganiser les sections"""
        for item in section_orders:
            await self.db.section.update(
                where={'id': item['id']},
                data={'order': item['order']}
            )
        return True
    
    # ========== LESSONS ==========
    
    async def create_lesson(self, section_id: str, data: Dict[str, Any]) -> Dict:
        """Créer une leçon"""
        lesson = await self.db.lesson.create(data={
            'sectionId': section_id,
            'title': data['title'],
            'description': data.get('description'),
            'content': data.get('content'),
            'order': data['order'],
            'videoUrl': data.get('videoUrl'),
            'videoDuration': data.get('videoDuration'),
            'isFree': data.get('isFree', False)
        })
        
        # Mettre à jour la durée de la section
        await self._update_section_duration(section_id)
        
        return lesson
    
    async def get_lesson_by_id(self, lesson_id: str) -> Optional[Dict]:
        """Récupérer une leçon"""
        lesson = await self.db.lesson.find_unique(
            where={'id': lesson_id},
            include={'resources': True}
        )
        return lesson
    
    async def update_lesson(self, lesson_id: str, data: Dict[str, Any]) -> Dict:
        """Mettre à jour une leçon"""
        lesson = await self.db.lesson.update(
            where={'id': lesson_id},
            data=data
        )
        
        # Mettre à jour la durée de la section
        await self._update_section_duration(lesson['sectionId'])
        
        return lesson
    
    async def delete_lesson(self, lesson_id: str) -> bool:
        """Supprimer une leçon"""
        lesson = await self.db.lesson.find_unique(where={'id': lesson_id})
        section_id = lesson['sectionId']
        
        await self.db.lesson.delete(where={'id': lesson_id})
        
        # Mettre à jour la durée de la section
        await self._update_section_duration(section_id)
        
        return True
    
    async def _update_section_duration(self, section_id: str):
        """Calculer et mettre à jour la durée d'une section"""
        lessons = await self.db.lesson.find_many(
            where={'sectionId': section_id}
        )
        
        total_duration = sum(
            lesson.get('videoDuration', 0) or 0 
            for lesson in lessons
        )
        
        await self.db.section.update(
            where={'id': section_id},
            data={'duration': total_duration}
        )
    
    # ========== RESOURCES ==========
    
    async def add_resource(self, lesson_id: str, data: Dict[str, Any]) -> Dict:
        """Ajouter une ressource"""
        resource = await self.db.resource.create(data={
            'lessonId': lesson_id,
            'title': data['title'],
            'type': data['type'],
            'url': data['url'],
            'fileSize': data.get('fileSize'),
            'isDownloadable': data.get('isDownloadable', True)
        })
        return resource
    
    async def update_resource(self, resource_id: str, data: Dict[str, Any]) -> Dict:
        """Mettre à jour une ressource"""
        resource = await self.db.resource.update(
            where={'id': resource_id},
            data=data
        )
        return resource
    
    async def delete_resource(self, resource_id: str) -> bool:
        """Supprimer une ressource"""
        await self.db.resource.delete(where={'id': resource_id})
        return True
    
    async def increment_download_count(self, resource_id: str) -> Dict:
        """Incrémenter le compteur de téléchargements"""
        resource = await self.db.resource.update(
            where={'id': resource_id},
            data={'downloadCount': {'increment': 1}}
        )
        return resource
    
    # ========== CATEGORIES ==========
    
    async def create_category(self, data: Dict[str, Any]) -> Dict:
        """Créer une catégorie"""
        slug = slugify(data['name'])
        
        category = await self.db.category.create(data={
            'name': data['name'],
            'slug': slug,
            'description': data.get('description'),
            'imageUrl': data.get('imageUrl'),
            'isActive': data.get('isActive', True)
        })
        return category
    
    async def list_categories(self, is_active: Optional[bool] = None) -> List[Dict]:
        """Lister les catégories"""
        where = {}
        if is_active is not None:
            where['isActive'] = is_active
        
        categories = await self.db.category.find_many(
            where=where,
            order_by={'name': 'asc'}
        )
        return categories
    
    async def update_category(self, category_id: str, data: Dict[str, Any]) -> Dict:
        """Mettre à jour une catégorie"""
        category = await self.db.category.update(
            where={'id': category_id},
            data=data
        )
        return category
    
    # ========== TAGS ==========
    
    async def create_tag(self, name: str) -> Dict:
        """Créer un tag"""
        slug = slugify(name)
        
        tag = await self.db.tag.create(data={
            'name': name,
            'slug': slug
        })
        return tag
    
    async def list_tags(self, limit: Optional[int] = None) -> List[Dict]:
        """Lister les tags"""
        query = {
            'order_by': {'usageCount': 'desc'}
        }
        if limit:
            query['take'] = limit
        
        tags = await self.db.tag.find_many(**query)
        return tags
    
    # ========== WISHLIST ==========
    
    async def add_to_wishlist(self, student_id: str, course_id: str) -> Dict:
        """Ajouter à la wishlist"""
        wishlist_item = await self.db.wishlist.create(data={
            'studentId': student_id,
            'courseId': course_id
        })
        return wishlist_item
    
    async def remove_from_wishlist(self, student_id: str, course_id: str) -> bool:
        """Retirer de la wishlist"""
        await self.db.wishlist.delete_many(where={
            'studentId': student_id,
            'courseId': course_id
        })
        return True
    
    async def get_wishlist(self, student_id: str) -> List[Dict]:
        """Récupérer la wishlist"""
        # Note: Prisma Python ne supporte pas encore include sur les relations implicites
        # Il faut faire 2 requêtes
        wishlist_items = await self.db.wishlist.find_many(
            where={'studentId': student_id}
        )
        
        # Récupérer les cours
        course_ids = [item['courseId'] for item in wishlist_items]
        courses = await self.db.course.find_many(
            where={'id': {'in': course_ids}}
        )
        
        # Combiner les résultats
        courses_map = {course['id']: course for course in courses}
        for item in wishlist_items:
            item['course'] = courses_map.get(item['courseId'])
        
        return wishlist_items
    
    # ========== STATISTICS (pour événements externes) ==========
    
    async def increment_enrollment_count(self, course_id: str) -> Dict:
        """Incrémenter enrollmentCount (appelé par enrollments-service)"""
        course = await self.db.course.update(
            where={'id': course_id},
            data={'enrollmentCount': {'increment': 1}}
        )
        return course
    
    async def decrement_enrollment_count(self, course_id: str) -> Dict:
        """Décrémenter enrollmentCount"""
        course = await self.db.course.update(
            where={'id': course_id},
            data={'enrollmentCount': {'decrement': 1}}
        )
        return course
    
    async def increment_completion_count(self, course_id: str) -> Dict:
        """Incrémenter completionCount (appelé par enrollments-service)"""
        course = await self.db.course.update(
            where={'id': course_id},
            data={'completionCount': {'increment': 1}}
        )
        return course
    
    async def update_course_rating(self, course_id: str, new_rating: float) -> Dict:
        """Mettre à jour la note (appelé par reviews-service)"""
        course = await self.db.course.update(
            where={'id': course_id},
            data={
                'rating': new_rating,
                'reviewCount': {'increment': 1}
            }
        )
        return course