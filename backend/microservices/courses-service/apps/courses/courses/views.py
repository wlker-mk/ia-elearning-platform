from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import (
from .services import CoursesService
from .permissions import IsInstructor, IsOwnerOrReadOnly
import asyncio

    CourseListSerializer, CourseDetailSerializer,
    CourseCreateSerializer, CourseUpdateSerializer,
    SectionSerializer, SectionCreateSerializer,
    LessonSerializer, LessonCreateSerializer,
    ResourceSerializer, ResourceCreateSerializer,
    CategorySerializer, TagSerializer, WishlistSerializer
)
class CoursesViewSet(viewsets.ViewSet):
    """ViewSet pour la gestion des cours"""

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        elif self.action == 'create':
            return [IsAuthenticated(), IsInstructor()]
        return [IsAuthenticated()]

    def _run_async(self, coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def list(self, request):
        """Lister les cours"""
        service = CoursesService()

        async def _list():
            await service.connect()
            try:
                skip = int(request.query_params.get('skip', 0))
                take = int(request.query_params.get('take', 20))

                filters = {}
                if request.query_params.get('instructorId'):
                    filters['instructorId'] = request.query_params['instructorId']
                if request.query_params.get('categoryId'):
                    filters['categoryId'] = request.query_params['categoryId']
                if request.query_params.get('difficulty'):
                    filters['difficulty'] = request.query_params['difficulty']
                if request.query_params.get('isFree'):
                    filters['isFree'] = request.query_params['isFree'] == 'true'
                if request.query_params.get('search'):
                    filters['search'] = request.query_params['search']
                if request.query_params.get('published'):
                    filters['published'] = request.query_params['published'] == 'true'

                return await service.list_courses(skip, take, filters)
            finally:
                await service.disconnect()

        result = self._run_async(_list())
        serializer = CourseListSerializer(result['courses'], many=True)

        return Response({
            'results': serializer.data,
            'total': result['total'],
            'skip': result['skip'],
            'take': result['take']
        })

    def create(self, request):
        """Créer un cours"""
        serializer = CourseCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        service = CoursesService()

        async def _create():
            await service.connect()
            try:
                return await service.create_course(
                    serializer.validated_data,
                    str(request.user.id)
                )
            finally:
                await service.disconnect()

        course = self._run_async(_create())
        response_serializer = CourseDetailSerializer(course)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Récupérer un cours"""
        service = CoursesService()

        async def _retrieve():
            await service.connect()
            try:
                # Essayer par ID puis par slug
                course = await service.get_course_by_id(pk)
                if not course:
                    course = await service.get_course_by_slug(pk)
                return course
            finally:
                await service.disconnect()

        course = self._run_async(_retrieve())

        if not course:
            return Response(
                {'error': 'Course not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CourseDetailSerializer(course)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """Mettre à jour un cours"""
        serializer = CourseUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        service = CoursesService()

        async def _update():
            await service.connect()
            try:
                return await service.update_course(pk, serializer.validated_data)
            finally:
                await service.disconnect()

        course = self._run_async(_update())

        if not course:
            return Response(
                {'error': 'Course not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        response_serializer = CourseDetailSerializer(course)
        return Response(response_serializer.data)

    def destroy(self, request, pk=None):
        """Supprimer un cours"""
        service = CoursesService()

        async def _delete():
            await service.connect()
            try:
                return await service.delete_course(pk)
            finally:
                await service.disconnect()

        self._run_async(_delete())
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publier un cours"""
        service = CoursesService()

        async def _publish():
            await service.connect()
            try:
                return await service.publish_course(pk)
            finally:
                await service.disconnect()

        course = self._run_async(_publish())
        serializer = CourseListSerializer(course)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        """Dépublier un cours"""
        service = CoursesService()

        async def _unpublish():
            await service.connect()
            try:
                return await service.unpublish_course(pk)
            finally:
                await service.disconnect()

        course = self._run_async(_unpublish())
        serializer = CourseListSerializer(course)
        return Response(serializer.data)


class SectionsViewSet(viewsets.ViewSet):
    """ViewSet pour les sections"""
    permission_classes = [IsAuthenticated]

    def _run_async(self, coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def create(self, request):
        """Créer une section"""
        serializer = SectionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        course_id = request.data.get('courseId')
        if not course_id:
            return Response(
                {'error': 'courseId is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = CoursesService()

        async def _create():
            await service.connect()
            try:
                return await service.create_section(course_id, serializer.validated_data)
            finally:
                await service.disconnect()

        section = self._run_async(_create())
        response_serializer = SectionSerializer(section)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        """Mettre à jour une section"""
        service = CoursesService()

        async def _update():
            await service.connect()
            try:
                return await service.update_section(pk, request.data)
            finally:
                await service.disconnect()

        section = self._run_async(_update())
        serializer = SectionSerializer(section)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """Supprimer une section"""
        service = CoursesService()

        async def _delete():
            await service.connect()
            try:
                return await service.delete_section(pk)
            finally:
                await service.disconnect()

        self._run_async(_delete())
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """Réorganiser les sections"""
        course_id = request.data.get('courseId')
        section_orders = request.data.get('sections', [])

        if not course_id or not section_orders:
            return Response(
                {'error': 'courseId and sections are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = CoursesService()

        async def _reorder():
            await service.connect()
            try:
                return await service.reorder_sections(course_id, section_orders)
            finally:
                await service.disconnect()

        self._run_async(_reorder())
        return Response({'message': 'Sections reordered successfully'})


class LessonsViewSet(viewsets.ViewSet):
    """ViewSet pour les leçons"""
    permission_classes = [IsAuthenticated]

    def _run_async(self, coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def retrieve(self, request, pk=None):
        """Récupérer une leçon"""
        service = CoursesService()

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

        serializer = LessonSerializer(lesson)
        return Response(serializer.data)

    def create(self, request):
        """Créer une leçon"""
        serializer = LessonCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        section_id = request.data.get('sectionId')
        if not section_id:
            return Response(
                {'error': 'sectionId is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = CoursesService()

        async def _create():
            await service.connect()
            try:
                return await service.create_lesson(section_id, serializer.validated_data)
            finally:
                await service.disconnect()

        lesson = self._run_async(_create())
        response_serializer = LessonSerializer(lesson)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        """Mettre à jour une leçon"""
        service = CoursesService()

        async def _update():
            await service.connect()
            try:
                return await service.update_lesson(pk, request.data)
            finally:
                await service.disconnect()

        lesson = self._run_async(_update())
        serializer = LessonSerializer(lesson)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """Supprimer une leçon"""
        service = CoursesService()

        async def _delete():
            await service.connect()
            try:
                return await service.delete_lesson(pk)
            finally:
                await service.disconnect()

        self._run_async(_delete())
        return Response(status=status.HTTP_204_NO_CONTENT)


class ResourcesViewSet(viewsets.ViewSet):
    """ViewSet pour les ressources"""
    permission_classes = [IsAuthenticated]

    def _run_async(self, coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def create(self, request):
        """Ajouter une ressource"""
        serializer = ResourceCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        lesson_id = request.data.get('lessonId')
        if not lesson_id:
            return Response(
                {'error': 'lessonId is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = CoursesService()

        async def _create():
            await service.connect()
            try:
                return await service.add_resource(lesson_id, serializer.validated_data)
            finally:
                await service.disconnect()

        resource = self._run_async(_create())
        response_serializer = ResourceSerializer(resource)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        """Mettre à jour une ressource"""
        service = CoursesService()

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
        service = CoursesService()

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
        service = CoursesService()

        async def _track():
            await service.connect()
            try:
                return await service.increment_download_count(pk)
            finally:
                await service.disconnect()

        self._run_async(_track())
        return Response({'message': 'Download tracked'})


class CategoriesViewSet(viewsets.ViewSet):
    """ViewSet pour les catégories"""

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), IsInstructor()]

    def _run_async(self, coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def list(self, request):
        """Lister les catégories"""
        service = CoursesService()

        async def _list():
            await service.connect()
            try:
                is_active = request.query_params.get('isActive')
                if is_active:
                    is_active = is_active == 'true'
                return await service.list_categories(is_active)
            finally:
                await service.disconnect()

        categories = self._run_async(_list())
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Créer une catégorie"""
        serializer = CategorySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        service = CoursesService()

        async def _create():
            await service.connect()
            try:
                return await service.create_category(serializer.validated_data)
            finally:
                await service.disconnect()

        category = self._run_async(_create())
        response_serializer = CategorySerializer(category)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        """Mettre à jour une catégorie"""
        service = CoursesService()

        async def _update():
            await service.connect()
            try:
                return await service.update_category(pk, request.data)
            finally:
                await service.disconnect()

        category = self._run_async(_update())
        serializer = CategorySerializer(category)
        return Response(serializer.data)


class TagsViewSet(viewsets.ViewSet):
    """ViewSet pour les tags"""
    permission_classes = [AllowAny]

    def _run_async(self, coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def list(self, request):
        """Lister les tags"""
        service = CoursesService()
        limit = request.query_params.get('limit')
        if limit:
            limit = int(limit)

        async def _list():
            await service.connect()
            try:
                return await service.list_tags(limit)
            finally:
                await service.disconnect()

        tags = self._run_async(_list())
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)


class WishlistViewSet(viewsets.ViewSet):
    """ViewSet pour la wishlist"""
    permission_classes = [IsAuthenticated]

    def _run_async(self, coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def list(self, request):
        """Ma wishlist"""
        service = CoursesService()

        async def _list():
            await service.connect()
            try:
                return await service.get_wishlist(str(request.user.id))
            finally:
                await service.disconnect()

        wishlist = self._run_async(_list())
        serializer = WishlistSerializer(wishlist, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        """Ajouter à la wishlist"""
        course_id = request.data.get('courseId')

        if not course_id:
            return Response(
                {'error': 'courseId is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = CoursesService()

        async def _add():
            await service.connect()
            try:
                return await service.add_to_wishlist(
                    str(request.user.id),
                    course_id
                )
            finally:
                await service.disconnect()

        wishlist_item = self._run_async(_add())
        serializer = WishlistSerializer(wishlist_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'])
    def remove(self, request):
        """Retirer de la wishlist"""
        course_id = request.query_params.get('courseId')

        if not course_id:
            return Response(
                {'error': 'courseId is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = CoursesService()

        async def _remove():
            await service.connect()
            try:
                return await service.remove_from_wishlist(
                    str(request.user.id),
                    course_id
                )
            finally:
                await service.disconnect()

        self._run_async(_remove())
        return Response(status=status.HTTP_204_NO_CONTENT)
