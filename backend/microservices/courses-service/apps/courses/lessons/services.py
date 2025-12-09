from typing import List, Optional, Dict, Any
from prisma import Prisma

class LessonsService:
    def __init__(self):
        self.db = Prisma()
    
    async def connect(self):
        await self.db.connect()
    
    async def disconnect(self):
        await self.db.disconnect()
    
    # ========== LESSONS ==========
    
    async def create_lesson(self, data: Dict[str, Any]) -> Dict:
        """Créer une leçon"""
        lesson = await self.db.lesson.create(data={
            'sectionId': data['sectionId'],
            'title': data['title'],
            'description': data.get('description'),
            'content': data.get('content'),
            'order': data['order'],
            'videoUrl': data.get('videoUrl'),
            'videoDuration': data.get('videoDuration'),
            'isFree': data.get('isFree', False)
        })
        
        # Mettre à jour la durée de la section
        await self._update_section_duration(data['sectionId'])
        
        return lesson
    
    async def get_lesson_by_id(self, lesson_id: str) -> Optional[Dict]:
        """Récupérer une leçon avec ses ressources"""
        lesson = await self.db.lesson.find_unique(
            where={'id': lesson_id},
            include={'resources': True}
        )
        return lesson
    
    async def list_lessons_by_section(self, section_id: str) -> List[Dict]:
        """Lister les leçons d'une section"""
        lessons = await self.db.lesson.find_many(
            where={'sectionId': section_id},
            order_by={'order': 'asc'}
        )
        return lessons
    
    async def update_lesson(self, lesson_id: str, data: Dict[str, Any]) -> Dict:
        """Mettre à jour une leçon"""
        lesson = await self.db.lesson.update(
            where={'id': lesson_id},
            data=data
        )
        
        # Mettre à jour la durée de la section si videoDuration a changé
        if 'videoDuration' in data:
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
    
    async def reorder_lessons(self, section_id: str, lesson_orders: List[Dict]) -> bool:
        """Réorganiser les leçons d'une section"""
        for item in lesson_orders:
            await self.db.lesson.update(
                where={'id': item['id']},
                data={'order': item['order']}
            )
        return True
    
    async def duplicate_lesson(self, lesson_id: str, new_section_id: Optional[str] = None) -> Dict:
        """Dupliquer une leçon"""
        original = await self.get_lesson_by_id(lesson_id)
        
        if not original:
            raise ValueError('Lesson not found')
        
        # Créer la copie
        duplicate_data = {
            'sectionId': new_section_id or original['sectionId'],
            'title': f"{original['title']} (Copy)",
            'description': original.get('description'),
            'content': original.get('content'),
            'order': original['order'] + 1,  # Placer après l'original
            'videoUrl': original.get('videoUrl'),
            'videoDuration': original.get('videoDuration'),
            'isFree': original.get('isFree', False)
        }
        
        duplicate = await self.create_lesson(duplicate_data)
        
        # Dupliquer les ressources
        if original.get('resources'):
            for resource in original['resources']:
                await self.add_resource({
                    'lessonId': duplicate['id'],
                    'title': resource['title'],
                    'type': resource['type'],
                    'url': resource['url'],
                    'fileSize': resource.get('fileSize'),
                    'isDownloadable': resource.get('isDownloadable', True)
                })
        
        return duplicate
    
    async def _update_section_duration(self, section_id: str):
        """Calculer et mettre à jour la durée totale d'une section"""
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
    
    async def add_resource(self, data: Dict[str, Any]) -> Dict:
        """Ajouter une ressource à une leçon"""
        resource = await self.db.resource.create(data={
            'lessonId': data['lessonId'],
            'title': data['title'],
            'type': data['type'],
            'url': data['url'],
            'fileSize': data.get('fileSize'),
            'isDownloadable': data.get('isDownloadable', True)
        })
        return resource
    
    async def get_resource_by_id(self, resource_id: str) -> Optional[Dict]:
        """Récupérer une ressource"""
        resource = await self.db.resource.find_unique(
            where={'id': resource_id}
        )
        return resource
    
    async def list_resources_by_lesson(self, lesson_id: str) -> List[Dict]:
        """Lister les ressources d'une leçon"""
        resources = await self.db.resource.find_many(
            where={'lessonId': lesson_id},
            order_by={'createdAt': 'asc'}
        )
        return resources
    
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
    
    async def track_resource_download(self, resource_id: str) -> Dict:
        """Incrémenter le compteur de téléchargements"""
        resource = await self.db.resource.update(
            where={'id': resource_id},
            data={'downloadCount': {'increment': 1}}
        )
        return resource
    
    # ========== UTILITY METHODS ==========
    
    async def get_lesson_count_by_course(self, course_id: str) -> int:
        """Compter le nombre total de leçons d'un cours"""
        # Récupérer toutes les sections du cours
        sections = await self.db.section.find_many(
            where={'courseId': course_id}
        )
        
        section_ids = [section['id'] for section in sections]
        
        # Compter les leçons
        count = await self.db.lesson.count(
            where={'sectionId': {'in': section_ids}}
        )
        
        return count
    
    async def get_free_lessons_by_course(self, course_id: str) -> List[Dict]:
        """Récupérer toutes les leçons gratuites d'un cours (preview)"""
        sections = await self.db.section.find_many(
            where={'courseId': course_id}
        )
        
        section_ids = [section['id'] for section in sections]
        
        lessons = await self.db.lesson.find_many(
            where={
                'sectionId': {'in': section_ids},
                'isFree': True
            },
            order_by={'order': 'asc'}
        )
        
        return lessons
    
    async def validate_lesson_access(
        self, 
        lesson_id: str, 
        user_id: str, 
        has_enrollment: bool
    ) -> Dict:
        """Valider si un utilisateur peut accéder à une leçon"""
        lesson = await self.get_lesson_by_id(lesson_id)
        
        if not lesson:
            return {'hasAccess': False, 'reason': 'Lesson not found'}
        
        # Les leçons gratuites sont accessibles à tous
        if lesson.get('isFree'):
            return {'hasAccess': True, 'reason': 'Free lesson'}
        
        # Les autres leçons nécessitent une inscription
        if has_enrollment:
            return {'hasAccess': True, 'reason': 'Enrolled'}
        
        return {'hasAccess': False, 'reason': 'Enrollment required'}
    
    async def get_next_lesson(self, current_lesson_id: str) -> Optional[Dict]:
        """Récupérer la leçon suivante"""
        current = await self.db.lesson.find_unique(
            where={'id': current_lesson_id}
        )
        
        if not current:
            return None
        
        # Chercher la prochaine leçon dans la même section
        next_in_section = await self.db.lesson.find_first(
            where={
                'sectionId': current['sectionId'],
                'order': {'gt': current['order']}
            },
            order_by={'order': 'asc'}
        )
        
        if next_in_section:
            return next_in_section
        
        # Si pas de leçon suivante dans cette section, 
        # chercher la première leçon de la section suivante
        current_section = await self.db.section.find_unique(
            where={'id': current['sectionId']}
        )
        
        next_section = await self.db.section.find_first(
            where={
                'courseId': current_section['courseId'],
                'order': {'gt': current_section['order']}
            },
            order_by={'order': 'asc'}
        )
        
        if next_section:
            first_lesson = await self.db.lesson.find_first(
                where={'sectionId': next_section['id']},
                order_by={'order': 'asc'}
            )
            return first_lesson
        
        return None
    
    async def get_previous_lesson(self, current_lesson_id: str) -> Optional[Dict]:
        """Récupérer la leçon précédente"""
        current = await self.db.lesson.find_unique(
            where={'id': current_lesson_id}
        )
        
        if not current:
            return None
        
        # Chercher la leçon précédente dans la même section
        prev_in_section = await self.db.lesson.find_first(
            where={
                'sectionId': current['sectionId'],
                'order': {'lt': current['order']}
            },
            order_by={'order': 'desc'}
        )
        
        if prev_in_section:
            return prev_in_section
        
        # Si pas de leçon précédente dans cette section,
        # chercher la dernière leçon de la section précédente
        current_section = await self.db.section.find_unique(
            where={'id': current['sectionId']}
        )
        
        prev_section = await self.db.section.find_first(
            where={
                'courseId': current_section['courseId'],
                'order': {'lt': current_section['order']}
            },
            order_by={'order': 'desc'}
        )
        
        if prev_section:
            last_lesson = await self.db.lesson.find_first(
                where={'sectionId': prev_section['id']},
                order_by={'order': 'desc'}
            )
            return last_lesson
        
        return None