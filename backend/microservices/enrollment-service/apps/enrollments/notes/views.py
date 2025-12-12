from rest_framework.views import APIView
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from shared.shared.utils.responses import success_response, error_response
from .serializers import (
    NoteCreateSerializer,
    NoteUpdateSerializer,
    NoteSerializer,
    BookmarkCreateSerializer,
    BookmarkSerializer,
    CertificateSerializer,
    CertificateVerificationSerializer
)
from .services import NoteService, BookmarkService, CertificateService


class NoteListCreateView(APIView):
    """
    List all notes or create a new note
    """
    
    @extend_schema(
        summary="List notes",
        parameters=[
            OpenApiParameter('courseId', str, description='Filter by course'),
            OpenApiParameter('lessonId', str, description='Filter by lesson'),
            OpenApiParameter('type', str, description='Filter by type'),
        ],
        responses={200: NoteSerializer(many=True)}
    )
    def get(self, request):
        user_id = request.user_id
        course_id = request.query_params.get('courseId')
        lesson_id = request.query_params.get('lessonId')
        note_type = request.query_params.get('type')
        
        with NoteService() as service:
            notes = service.get_notes(
                user_id,
                course_id=course_id,
                lesson_id=lesson_id,
                note_type=note_type
            )
            serializer = NoteSerializer(notes, many=True)
            
            return success_response(
                data=serializer.data,
                message='Notes retrieved successfully'
            )
    
    @extend_schema(
        summary="Create note",
        request=NoteCreateSerializer,
        responses={201: NoteSerializer}
    )
    def post(self, request):
        user_id = request.user_id
        serializer = NoteCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                message='Invalid data',
                errors=serializer.errors
            )
        
        with NoteService() as service:
            note = service.create_note(user_id, serializer.validated_data)
            result_serializer = NoteSerializer(note)
            
            return success_response(
                data=result_serializer.data,
                message='Note created successfully',
                status_code=status.HTTP_201_CREATED
            )


class NoteDetailView(APIView):
    """
    Retrieve, update or delete a note
    """
    
    @extend_schema(
        summary="Get note details",
        responses={200: NoteSerializer}
    )
    def get(self, request, note_id):
        user_id = request.user_id
        
        with NoteService() as service:
            note = service.get_note(note_id, user_id)
            serializer = NoteSerializer(note)
            
            return success_response(
                data=serializer.data,
                message='Note retrieved successfully'
            )
    
    @extend_schema(
        summary="Update note",
        request=NoteUpdateSerializer,
        responses={200: NoteSerializer}
    )
    def patch(self, request, note_id):
        user_id = request.user_id
        serializer = NoteUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                message='Invalid data',
                errors=serializer.errors
            )
        
        with NoteService() as service:
            note = service.update_note(note_id, user_id, serializer.validated_data)
            result_serializer = NoteSerializer(note)
            
            return success_response(
                data=result_serializer.data,
                message='Note updated successfully'
            )
    
    @extend_schema(
        summary="Delete note",
        responses={200: dict}
    )
    def delete(self, request, note_id):
        user_id = request.user_id
        
        with NoteService() as service:
            service.delete_note(note_id, user_id)
            
            return success_response(
                message='Note deleted successfully'
            )


class LessonNotesView(APIView):
    """
    Get all notes for a specific lesson
    """
    
    @extend_schema(
        summary="Get lesson notes",
        responses={200: NoteSerializer(many=True)}
    )
    def get(self, request, lesson_id):
        user_id = request.user_id
        
        with NoteService() as service:
            notes = service.get_notes(user_id, lesson_id=lesson_id)
            serializer = NoteSerializer(notes, many=True)
            
            return success_response(
                data=serializer.data,
                message='Lesson notes retrieved successfully'
            )


class BookmarkListCreateView(APIView):
    """
    List all bookmarks or create a new bookmark
    """
    
    @extend_schema(
        summary="List bookmarks",
        parameters=[
            OpenApiParameter('courseId', str, description='Filter by course'),
            OpenApiParameter('lessonId', str, description='Filter by lesson'),
            OpenApiParameter('type', str, description='Filter by type'),
        ],
        responses={200: BookmarkSerializer(many=True)}
    )
    def get(self, request):
        user_id = request.user_id
        course_id = request.query_params.get('courseId')
        lesson_id = request.query_params.get('lessonId')
        bookmark_type = request.query_params.get('type')
        
        with BookmarkService() as service:
            bookmarks = service.get_bookmarks(
                user_id,
                course_id=course_id,
                lesson_id=lesson_id,
                bookmark_type=bookmark_type
            )
            serializer = BookmarkSerializer(bookmarks, many=True)
            
            return success_response(
                data=serializer.data,
                message='Bookmarks retrieved successfully'
            )
    
    @extend_schema(
        summary="Create bookmark",
        request=BookmarkCreateSerializer,
        responses={201: BookmarkSerializer}
    )
    def post(self, request):
        user_id = request.user_id
        serializer = BookmarkCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                message='Invalid data',
                errors=serializer.errors
            )
        
        with BookmarkService() as service:
            bookmark = service.create_bookmark(user_id, serializer.validated_data)
            result_serializer = BookmarkSerializer(bookmark)
            
            return success_response(
                data=result_serializer.data,
                message='Bookmark created successfully',
                status_code=status.HTTP_201_CREATED
            )


class BookmarkDetailView(APIView):
    """
    Retrieve or delete a bookmark
    """
    
    @extend_schema(
        summary="Get bookmark details",
        responses={200: BookmarkSerializer}
    )
    def get(self, request, bookmark_id):
        user_id = request.user_id
        
        with BookmarkService() as service:
            bookmark = service.get_bookmark(bookmark_id, user_id)
            serializer = BookmarkSerializer(bookmark)
            
            return success_response(
                data=serializer.data,
                message='Bookmark retrieved successfully'
            )
    
    @extend_schema(
        summary="Delete bookmark",
        responses={200: dict}
    )
    def delete(self, request, bookmark_id):
        user_id = request.user_id
        
        with BookmarkService() as service:
            service.delete_bookmark(bookmark_id, user_id)
            
            return success_response(
                message='Bookmark deleted successfully'
            )


class CertificateListView(APIView):
    """
    List all certificates for current user
    """
    
    @extend_schema(
        summary="List certificates",
        responses={200: CertificateSerializer(many=True)}
    )
    def get(self, request):
        user_id = request.user_id
        
        with CertificateService() as service:
            certificates = service.get_student_certificates(user_id)
            serializer = CertificateSerializer(certificates, many=True)
            
            return success_response(
                data=serializer.data,
                message='Certificates retrieved successfully'
            )


class CertificateDetailView(APIView):
    """
    Get certificate details
    """
    
    @extend_schema(
        summary="Get certificate details",
        responses={200: CertificateSerializer}
    )
    def get(self, request, certificate_id):
        with CertificateService() as service:
            certificate = service.get_certificate(certificate_id)
            serializer = CertificateSerializer(certificate)
            
            return success_response(
                data=serializer.data,
                message='Certificate retrieved successfully'
            )


class VerifyCertificateView(APIView):
    """
    Verify certificate by verification code
    """
    
    @extend_schema(
        summary="Verify certificate",
        responses={200: CertificateVerificationSerializer}
    )
    def get(self, request, verification_code):
        with CertificateService() as service:
            result = service.verify_certificate(verification_code)
            serializer = CertificateVerificationSerializer(result)
            
            return success_response(
                data=serializer.data,
                message=result['message']
            )