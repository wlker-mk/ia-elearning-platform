from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import (
    LessonContentSerializer, LessonListSerializer,
    LessonCreateSerializer, LessonUpdateSerializer,
    ResourceSerializer, ResourceCreateSerializer,
    LessonWithResourcesSerializer, BulkLessonOrderSerializer
)
from .services import LessonsService
from apps.courses.permissions import IsCourseInstructor
import asyncio

class LessonsViewSet(viewsets.ViewSet):
    """ViewSet pour les leçons"""
    
    def get_permissions(self):
        if self.action in ['retrieve', 'list']:
            return [AllowAny()]
        return [IsAuthenticated(), IsCourseInstructor()]
    
    def _run_async(self, coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    def list(self, request):
        """Lister les leçons d'une section"""
        section_id = request.query_params.get('sectionId')
        
        if not section_id:
            return Response(
                {'error': 'sectionId is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = LessonsService()
        
        async def _list():
            await service.connect()
            try:
                return await service.list_lessons_by_section(section_id)
            finally:
                await service.disconnect()
        
        lessons = self._run_async(_list())
        serializer = LessonListSerializer(lessons, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        """Créer une leçon"""
        serializer = LessonCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        service = LessonsService()
        
        async def _create():
            await service.connect()
            try:
                return await service.create_lesson(serializer.validated_data)
            finally:
                await service.disconnect()
        
        lesson = self._run_async(_create())
        response_serializer = LessonContentSerializer(lesson)
        
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None):
        """Récupérer une leçon"""
        service = LessonsService()
        
        async def _retrieve():
            await service.connect()
            try:
                return await service.get_lesson_by_id(pk)
            finally:
                await service.disconnect()
        
        lesson = self._run_async(_retrieve())
        
        if not lesson:
            return Response(
                {'error': 'Lesson not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = LessonWithResourcesSerializer(lesson)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """Mettre à jour une leçon"""
        serializer = LessonUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        service = LessonsService()
        
        async def _update():
            await service.connect()
            try:
                return await service.update_lesson(pk, serializer.validated_data)
            finally:
                await service.disconnect()
        
        lesson = self._run_async(_update())
        response_serializer = LessonContentSerializer(lesson)
        return Response(response_serializer.data)
    
    def destroy(self, request, pk=None):
        """Supprimer une leçon"""
        service = LessonsService()
        
        async def _delete():
            await service.connect()
            try:
                return await service.delete_lesson(pk)
            finally:
                await service.disconnect()
        
        self._run_async(_delete())
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """Réorganiser les leçons"""
        serializer = BulkLessonOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        section_id = request.data.get('sectionId')
        lessons = serializer.validated_data['lessons']
        
        if not section_id:
            return Response(
                {'error': 'sectionId is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = LessonsService()
        
        async def _reorder():
            await service.connect()
            try:
                return await service.reorder_lessons(section_id, lessons)
            finally:
                await service.disconnect()
        
        self._run_async(_reorder())
        return Response({'message': 'Lessons reordered successfully'})
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Dupliquer une leçon"""
        new_section_id = request.data.get('newSectionId')
        
        service = LessonsService()
        
        async def _duplicate():
            await service.connect()
            try:
                return await service.duplicate_lesson(pk, new_section_id)
            finally:
                await service.disconnect()
        
        duplicate = self._run_async(_duplicate())
        serializer = LessonContentSerializer(duplicate)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def next(self, request, pk=None):
        """Récupérer la leçon suivante"""
        service = LessonsService()
        
        async def _next():
            await service.connect()
            try:
                return await service.get_next_lesson(pk)
            finally:
                await service.disconnect()
        
        next_lesson = self._run_async(_next())
        
        if not next_lesson:
            return Response({'message': 'No next lesson'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = LessonListSerializer(next_lesson)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def previous(self, request, pk=None):
        """Récupérer la leçon précédente"""
        service = LessonsService()
        
        async def _previous():
            await service.connect()
            try:
                return await service.get_previous_lesson(pk)
            finally:
                await service.disconnect()
        
        prev_lesson = self._run_async(_previous())
        
        if not prev_lesson:
            return Response({'message': 'No previous lesson'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = LessonListSerializer(prev_lesson)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def validate_access(self, request, pk=None):
        """Valider l'accès à une leçon"""
        user_id = str(request.user.id) if request.user.is_authenticated else None
        has_enrollment = request.data.get('hasEnrollment', False)
        
        service = LessonsService()
        
        async def _validate():
            await service.connect()
            try:
                return await service.validate_lesson_access(
                    pk, 
                    user_id, 
                    has_enrollment
                )
            finally:
                await service.disconnect()
        
        result = self._run_async(_validate())
        return Response(result)


class ResourcesViewSet(viewsets.ViewSet):
    """ViewSet pour les ressources"""
    permission_classes = [IsAuthenticated, IsCourseInstructor]
    
    def _run_async(self, coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    def list(self, request):
        """Lister les ressources d'une leçon"""
        lesson_id = request.query_params.get('lessonId')
        
        if not lesson_id:
            return Response(
                {'error': 'lessonId is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = LessonsService()
        
        async def _list():
            await service.connect()
            try:
                return await service.list_resources_by_lesson(lesson_id)
            finally:
                await service.disconnect()
        
        resources = self._run_async(_list())
        serializer = ResourceSerializer(resources, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        """Ajouter une ressource"""
        serializer = ResourceCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        service = LessonsService()
        
        async def _create():
            await service.connect()
            try:
                return await service.add_resource(serializer.validated_data)
            finally:
                await service.disconnect()
        
        resource = self._run_async(_create())
        response_serializer = ResourceSerializer(resource)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None):
        """Récupérer une ressource"""
        service = LessonsService()
        
        async def _retrieve():
            await service.connect()
            try:
                return await service.get_resource_by_id(pk)
            finally:
                await service.disconnect()
        
        resource = self._run_async(_retrieve())
        
        if not resource:
            return Response(
                {'error': 'Resource not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ResourceSerializer(resource)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """Mettre à jour une ressource"""
        service = LessonsService()
        
        async def _update():
            await service.connect()
            try:
                return await service.update_resource(pk, request.data)
            finally:
                await service.disconnect()
        
        resource = self._run_async(_update())
        serializer = ResourceSerializer(resource)
        return Response(serializer.data)
    
    def destroy(self, request, pk=None):
        """Supprimer une ressource"""
        service = LessonsService()
        
        async def _delete():
            await service.connect()
            try:
                return await service.delete_resource(pk)
            finally:
                await service.disconnect()
        
        self._run_async(_delete())
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def track_download(self, request, pk=None):
        """Tracker un téléchargement"""
        service = LessonsService()
        
        async def _track():
            await service.connect()
            try:
                return await service.track_resource_download(pk)
            finally:
                await service.disconnect()
        
        resource = self._run_async(_track())
        return Response({'downloadCount': resource['downloadCount']})