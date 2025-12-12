from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    QuizSerializer, QuizCreateSerializer, QuizUpdateSerializer,
    QuestionSerializer, QuizAttemptSerializer, QuizAttemptStartSerializer,
    QuizAttemptSubmitSerializer, ProctoringSessionSerializer,
    ProctoringEventSerializer, QuizStatisticsSerializer
)
from .services import QuizzesService
from .permissions import IsInstructor, IsOwnerOrReadOnly
import asyncio
from asgiref.sync import async_to_sync


class QuizViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = QuizzesService()
    
    def _run_async(self, coro):
        """Helper to run async functions"""
        return async_to_sync(coro)()
    
    def list(self, request):
        """List all quizzes or filter by lesson/course"""
        lesson_id = request.query_params.get('lesson_id')
        course_id = request.query_params.get('course_id')
        
        async def _list():
            await self.service.connect()
            try:
                if lesson_id:
                    quizzes = await self.service.get_quizzes_by_lesson(lesson_id)
                elif course_id:
                    quizzes = await self.service.get_quizzes_by_course(course_id)
                else:
                    return Response(
                        {'error': 'Please provide lesson_id or course_id'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                serializer = QuizSerializer(quizzes, many=True)
                return Response(serializer.data)
            finally:
                await self.service.disconnect()
        
        return self._run_async(_list)
    
    def create(self, request):
        """Create a new quiz"""
        serializer = QuizCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        async def _create():
            await self.service.connect()
            try:
                quiz = await self.service.create_quiz(
                    serializer.validated_data,
                    serializer.validated_data.get('questions', [])
                )
                result_serializer = QuizSerializer(quiz)
                return Response(result_serializer.data, status=status.HTTP_201_CREATED)
            finally:
                await self.service.disconnect()
        
        return self._run_async(_create)
    
    def retrieve(self, request, pk=None):
        """Get a specific quiz"""
        async def _retrieve():
            await self.service.connect()
            try:
                quiz = await self.service.get_quiz_by_id(pk)
                if not quiz:
                    return Response(
                        {'error': 'Quiz not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                serializer = QuizSerializer(quiz)
                return Response(serializer.data)
            finally:
                await self.service.disconnect()
        
        return self._run_async(_retrieve)
    
    def update(self, request, pk=None):
        """Update a quiz"""
        serializer = QuizUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        async def _update():
            await self.service.connect()
            try:
                quiz = await self.service.update_quiz(pk, serializer.validated_data)
                result_serializer = QuizSerializer(quiz)
                return Response(result_serializer.data)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            finally:
                await self.service.disconnect()
        
        return self._run_async(_update)
    
    def destroy(self, request, pk=None):
        """Delete a quiz"""
        async def _delete():
            await self.service.connect()
            try:
                await self.service.delete_quiz(pk)
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            finally:
                await self.service.disconnect()
        
        return self._run_async(_delete)
    
    @action(detail=True, methods=['post'])
    def add_question(self, request, pk=None):
        """Add a question to a quiz"""
        serializer = QuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        async def _add_question():
            await self.service.connect()
            try:
                question = await self.service.create_question(pk, serializer.validated_data)
                result_serializer = QuestionSerializer(question)
                return Response(result_serializer.data, status=status.HTTP_201_CREATED)
            finally:
                await self.service.disconnect()
        
        return self._run_async(_add_question)
    
    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """Get all questions for a quiz"""
        randomize = request.query_params.get('randomize', 'false').lower() == 'true'
        
        async def _get_questions():
            await self.service.connect()
            try:
                questions = await self.service.get_questions_by_quiz(pk, randomize=randomize)
                serializer = QuestionSerializer(questions, many=True)
                return Response(serializer.data)
            finally:
                await self.service.disconnect()
        
        return self._run_async(_get_questions)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get quiz statistics"""
        async def _get_statistics():
            await self.service.connect()
            try:
                stats = await self.service.get_quiz_statistics(pk)
                serializer = QuizStatisticsSerializer(stats)
                return Response(serializer.data)
            finally:
                await self.service.disconnect()
        
        return self._run_async(_get_statistics)
    
    @action(detail=True, methods=['get'])
    def attempts(self, request, pk=None):
        """Get all attempts for a quiz"""
        async def _get_attempts():
            await self.service.connect()
            try:
                attempts = await self.service.get_quiz_attempts(pk)
                serializer = QuizAttemptSerializer(attempts, many=True)
                return Response(serializer.data)
            finally:
                await self.service.disconnect()
        
        return self._run_async(_get_attempts)


class QuestionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsInstructor]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = QuizzesService()
    
    def _run_async(self, coro):
        return async_to_sync(coro)()
    
    def update(self, request, pk=None):
        """Update a question"""
        serializer = QuestionSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        async def _update():
            await self.service.connect()
            try:
                question = await self.service.update_question(pk, serializer.validated_data)
                result_serializer = QuestionSerializer(question)
                return Response(result_serializer.data)
            finally:
                await self.service.disconnect()
        
        return self._run_async(_update)
    
    def destroy(self, request, pk=None):
        """Delete a question"""
        async def _delete():
            await self.service.connect()
            try:
                await self.service.delete_question(pk)
                return Response(status=status.HTTP_204_NO_CONTENT)
            finally:
                await self.service.disconnect()
        
        return self._run_async(_delete)


class QuizAttemptViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = QuizzesService()
    
    def _run_async(self, coro):
        return async_to_sync(coro)()
    
    @action(detail=False, methods=['post'])
    def start(self, request):
        """Start a new quiz attempt"""
        serializer = QuizAttemptStartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        quiz_id = serializer.validated_data['quiz_id']
        student_id = str(request.user.id)
        
        async def _start():
            await self.service.connect()
            try:
                attempt = await self.service.start_quiz_attempt(quiz_id, student_id)
                # Create proctoring session
                await self.service.create_proctoring_session(attempt.id)
                result_serializer = QuizAttemptSerializer(attempt)
                return Response(result_serializer.data, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            finally:
                await self.service.disconnect()
        
        return self._run_async(_start)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit a quiz attempt"""
        serializer = QuizAttemptSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        async def _submit():
            await self.service.connect()
            try:
                attempt = await self.service.submit_quiz_attempt(
                    pk,
                    serializer.validated_data['answers']
                )
                result_serializer = QuizAttemptSerializer(attempt)
                return Response(result_serializer.data)
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            finally:
                await self.service.disconnect()
        
        return self._run_async(_submit)
    
    @action(detail=False, methods=['get'])
    def my_attempts(self, request):
        """Get current user's attempts for a quiz"""
        quiz_id = request.query_params.get('quiz_id')
        if not quiz_id:
            return Response(
                {'error': 'quiz_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        student_id = str(request.user.id)
        
        async def _get_attempts():
            await self.service.connect()
            try:
                attempts = await self.service.get_student_attempts(quiz_id, student_id)
                serializer = QuizAttemptSerializer(attempts, many=True)
                return Response(serializer.data)
            finally:
                await self.service.disconnect()
        
        return self._run_async(_get_attempts)


class ProctoringViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = QuizzesService()
    
    def _run_async(self, coro):
        return async_to_sync(coro)()
    
    @action(detail=False, methods=['post'])
    def record_event(self, request):
        """Record a proctoring event"""
        serializer = ProctoringEventSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        async def _record():
            await self.service.connect()
            try:
                session = await self.service.record_proctoring_event(
                    serializer.validated_data['quiz_attempt_id'],
                    serializer.validated_data['event_type'],
                    serializer.validated_data.get('details')
                )
                result_serializer = ProctoringSessionSerializer(session)
                return Response(result_serializer.data)
            finally:
                await self.service.disconnect()
        
        return self._run_async(_record)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsInstructor])
    def flagged(self, request):
        """Get all flagged proctoring sessions"""
        async def _get_flagged():
            await self.service.connect()
            try:
                sessions = await self.service.get_flagged_sessions()
                serializer = ProctoringSessionSerializer(sessions, many=True)
                return Response(serializer.data)
            finally:
                await self.service.disconnect()
        
        return self._run_async(_get_flagged)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsInstructor])
    def review(self, request, pk=None):
        """Review a proctoring session"""
        notes = request.data.get('notes', '')
        reviewer_id = str(request.user.id)
        
        async def _review():
            await self.service.connect()
            try:
                session = await self.service.review_proctoring_session(pk, reviewer_id, notes)
                serializer = ProctoringSessionSerializer(session)
                return Response(serializer.data)
            finally:
                await self.service.disconnect()
        
        return self._run_async(_review)