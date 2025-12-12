from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from shared.shared.utils.responses import success_response, error_response
from .serializers import (
    EnrollmentCreateSerializer,
    EnrollmentUpdateSerializer,
    EnrollmentSerializer,
    EnrollmentDetailSerializer,
    EnrollmentStatsSerializer
)
from .services import EnrollmentService


class EnrollmentListCreateView(APIView):
    """
    List all enrollments or create a new enrollment
    """
    
    @extend_schema(
        summary="List enrollments",
        parameters=[
            OpenApiParameter('status', str, description='Filter by status'),
            OpenApiParameter('courseId', str, description='Filter by course'),
        ],
        responses={200: EnrollmentSerializer(many=True)}
    )
    def get(self, request):
        user_id = request.user_id
        status_filter = request.query_params.get('status')
        course_id = request.query_params.get('courseId')
        
        with EnrollmentService() as service:
            enrollments = service.get_enrollments(
                student_id=user_id,
                status=status_filter,
                course_id=course_id
            )
            
            serializer = EnrollmentSerializer(enrollments, many=True)
            return success_response(
                data=serializer.data,
                message='Enrollments retrieved successfully'
            )
    
    @extend_schema(
        summary="Create enrollment",
        request=EnrollmentCreateSerializer,
        responses={201: EnrollmentSerializer}
    )
    def post(self, request):
        user_id = request.user_id
        serializer = EnrollmentCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                message='Invalid data',
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        with EnrollmentService() as service:
            enrollment = service.create_enrollment(user_id, serializer.validated_data)
            result_serializer = EnrollmentSerializer(enrollment)
            
            return success_response(
                data=result_serializer.data,
                message='Enrollment created successfully',
                status_code=status.HTTP_201_CREATED
            )


class EnrollmentDetailView(APIView):
    """
    Retrieve, update or delete an enrollment
    """
    
    @extend_schema(
        summary="Get enrollment details",
        responses={200: EnrollmentDetailSerializer}
    )
    def get(self, request, enrollment_id):
        user_id = request.user_id
        
        with EnrollmentService() as service:
            enrollment = service.get_enrollment_with_details(enrollment_id, user_id)
            serializer = EnrollmentDetailSerializer(enrollment)
            
            return success_response(
                data=serializer.data,
                message='Enrollment retrieved successfully'
            )
    
    @extend_schema(
        summary="Update enrollment",
        request=EnrollmentUpdateSerializer,
        responses={200: EnrollmentSerializer}
    )
    def patch(self, request, enrollment_id):
        user_id = request.user_id
        serializer = EnrollmentUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                message='Invalid data',
                errors=serializer.errors
            )
        
        with EnrollmentService() as service:
            enrollment = service.update_enrollment(
                enrollment_id, 
                user_id, 
                serializer.validated_data
            )
            result_serializer = EnrollmentSerializer(enrollment)
            
            return success_response(
                data=result_serializer.data,
                message='Enrollment updated successfully'
            )
    
    @extend_schema(
        summary="Cancel enrollment",
        responses={200: EnrollmentSerializer}
    )
    def delete(self, request, enrollment_id):
        user_id = request.user_id
        
        with EnrollmentService() as service:
            enrollment = service.cancel_enrollment(enrollment_id, user_id)
            serializer = EnrollmentSerializer(enrollment)
            
            return success_response(
                data=serializer.data,
                message='Enrollment cancelled successfully'
            )


class CompleteEnrollmentView(APIView):
    """
    Complete an enrollment
    """
    
    @extend_schema(
        summary="Complete enrollment",
        responses={200: EnrollmentSerializer}
    )
    def post(self, request, enrollment_id):
        user_id = request.user_id
        
        with EnrollmentService() as service:
            enrollment = service.complete_enrollment(enrollment_id, user_id)
            serializer = EnrollmentSerializer(enrollment)
            
            return success_response(
                data=serializer.data,
                message='Enrollment completed successfully. Certificate generation in progress.'
            )


class MyEnrollmentsView(APIView):
    """
    Get current user's enrollments
    """
    
    @extend_schema(
        summary="Get my enrollments",
        responses={200: EnrollmentSerializer(many=True)}
    )
    def get(self, request):
        user_id = request.user_id
        
        with EnrollmentService() as service:
            enrollments = service.get_enrollments(student_id=user_id)
            serializer = EnrollmentSerializer(enrollments, many=True)
            
            return success_response(
                data=serializer.data,
                message='Your enrollments retrieved successfully'
            )


class EnrollmentStatsView(APIView):
    """
    Get enrollment statistics for current user
    """
    
    @extend_schema(
        summary="Get enrollment statistics",
        responses={200: EnrollmentStatsSerializer}
    )
    def get(self, request):
        user_id = request.user_id
        
        with EnrollmentService() as service:
            stats = service.get_student_stats(user_id)
            serializer = EnrollmentStatsSerializer(stats)
            
            return success_response(
                data=serializer.data,
                message='Statistics retrieved successfully'
            )