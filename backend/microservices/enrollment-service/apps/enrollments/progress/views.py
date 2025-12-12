from rest_framework.views import APIView
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from shared.shared.utils.responses import success_response, error_response
from .serializers import (
    ProgressCreateUpdateSerializer,
    ProgressSerializer,
    CourseProgressSerializer,
    ProgressStatsSerializer,
    StudySessionCreateSerializer,
    StudySessionSerializer
)
from .services import ProgressService, StudySessionService


class ProgressCreateUpdateView(APIView):
    """
    Create or update progress for a lesson
    """
    
    @extend_schema(
        summary="Create or update progress",
        request=ProgressCreateUpdateSerializer,
        responses={200: ProgressSerializer}
    )
    def post(self, request):
        user_id = request.user_id
        serializer = ProgressCreateUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                message='Invalid data',
                errors=serializer.errors
            )
        
        with ProgressService() as service:
            progress = service.create_or_update_progress(
                user_id, 
                serializer.validated_data
            )
            result_serializer = ProgressSerializer(progress)
            
            return success_response(
                data=result_serializer.data,
                message='Progress updated successfully'
            )


class ProgressDetailView(APIView):
    """
    Get progress details
    """
    
    @extend_schema(
        summary="Get progress details",
        responses={200: ProgressSerializer}
    )
    def get(self, request, progress_id):
        user_id = request.user_id
        
        with ProgressService() as service:
            progress = service.get_progress(progress_id, user_id)
            serializer = ProgressSerializer(progress)
            
            return success_response(
                data=serializer.data,
                message='Progress retrieved successfully'
            )


class CourseProgressView(APIView):
    """
    Get all progress for a specific course
    """
    
    @extend_schema(
        summary="Get course progress",
        responses={200: CourseProgressSerializer}
    )
    def get(self, request, course_id):
        user_id = request.user_id
        
        with ProgressService() as service:
            progress = service.get_course_progress(user_id, course_id)
            serializer = CourseProgressSerializer(progress)
            
            return success_response(
                data=serializer.data,
                message='Course progress retrieved successfully'
            )


class ProgressStatsView(APIView):
    """
    Get overall progress statistics
    """
    
    @extend_schema(
        summary="Get progress statistics",
        responses={200: ProgressStatsSerializer}
    )
    def get(self, request):
        user_id = request.user_id
        
        with ProgressService() as service:
            stats = service.get_student_progress_stats(user_id)
            serializer = ProgressStatsSerializer(stats)
            
            return success_response(
                data=serializer.data,
                message='Statistics retrieved successfully'
            )


class StartStudySessionView(APIView):
    """
    Start a new study session
    """
    
    @extend_schema(
        summary="Start study session",
        request=StudySessionCreateSerializer,
        responses={201: StudySessionSerializer}
    )
    def post(self, request):
        user_id = request.user_id
        ip_address = request.META.get('REMOTE_ADDR')
        
        serializer = StudySessionCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                message='Invalid data',
                errors=serializer.errors
            )
        
        with StudySessionService() as service:
            session = service.start_session(
                user_id, 
                serializer.validated_data,
                ip_address
            )
            result_serializer = StudySessionSerializer(session)
            
            return success_response(
                data=result_serializer.data,
                message='Study session started',
                status_code=status.HTTP_201_CREATED
            )


class EndStudySessionView(APIView):
    """
    End an active study session
    """
    
    @extend_schema(
        summary="End study session",
        responses={200: StudySessionSerializer}
    )
    def post(self, request, session_id):
        user_id = request.user_id
        
        with StudySessionService() as service:
            session = service.end_session(session_id, user_id)
            serializer = StudySessionSerializer(session)
            
            return success_response(
                data=serializer.data,
                message='Study session ended'
            )


class ActiveStudySessionView(APIView):
    """
    Get active study session for a course
    """
    
    @extend_schema(
        summary="Get active study session",
        parameters=[
            OpenApiParameter('courseId', str, required=True)
        ],
        responses={200: StudySessionSerializer}
    )
    def get(self, request):
        user_id = request.user_id
        course_id = request.query_params.get('courseId')
        
        if not course_id:
            return error_response(
                message='courseId is required',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        with StudySessionService() as service:
            session = service.get_active_session(user_id, course_id)
            
            if not session:
                return success_response(
                    data=None,
                    message='No active session found'
                )
            
            serializer = StudySessionSerializer(session)
            return success_response(
                data=serializer.data,
                message='Active session retrieved'
            )