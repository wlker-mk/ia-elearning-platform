from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponseRedirect
from .serializers import (
from .services import CertificatesService
from apps.courses.courses.permissions import IsInstructor, IsAdminOrInstructor
import asyncio

        from datetime import datetime
    CertificateSerializer, CertificateCreateSerializer,
    CertificateVerificationSerializer, CertificateTemplateSerializer,
    CertificateTemplateCreateSerializer, CertificateStatsSerializer,
    BulkCertificateCreateSerializer, CertificateWithCourseSerializer
)
class CertificatesViewSet(viewsets.ViewSet):
    """ViewSet pour les certificats"""

    def get_permissions(self):
        if self.action == 'verify':
            return [AllowAny()]
        elif self.action in ['create', 'bulk_create']:
            return [IsAuthenticated(), IsInstructor()]
        return [IsAuthenticated()]

    def _run_async(self, coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    @action(detail=False, methods=['get'])
    def my_certificates(self, request):
        """Récupérer mes certificats"""
        service = CertificatesService()

        async def _list():
            await service.connect()
            try:
                return await service.get_user_certificates(str(request.user.id))
            finally:
                await service.disconnect()

        certificates = self._run_async(_list())
        serializer = CertificateWithCourseSerializer(certificates, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Générer un certificat"""
        serializer = CertificateCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        service = CertificatesService()

        async def _create():
            await service.connect()
            try:
                return await service.generate_certificate(
                    user_id=serializer.validated_data['userId'],
                    course_id=serializer.validated_data['courseId'],
                    completion_date=serializer.validated_data['completionDate'],
                    grade=serializer.validated_data.get('grade'),
                    metadata=serializer.validated_data.get('metadata')
                )
            finally:
                await service.disconnect()

        certificate = self._run_async(_create())
        response_serializer = CertificateSerializer(certificate)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Récupérer un certificat"""
        service = CertificatesService()

        async def _retrieve():
            await service.connect()
            try:
                return await service.get_certificate_by_id(pk)
            finally:
                await service.disconnect()

        certificate = self._run_async(_retrieve())

        if not certificate:
            return Response(
                {'error': 'Certificate not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Vérifier l'accès
        if str(certificate['userId']) != str(request.user.id):
            if not getattr(request.user, 'role', None) in ['admin', 'instructor']:
                return Response(
                    {'error': 'Access denied'},
                    status=status.HTTP_403_FORBIDDEN
                )

        serializer = CertificateSerializer(certificate)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def verify(self, request):
        """Vérifier un certificat (public)"""
        certificate_number = request.data.get('certificateNumber')

        if not certificate_number:
            return Response(
                {'error': 'certificateNumber is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = CertificatesService()

        # Récupérer IP et User-Agent
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT')

        async def _verify():
            await service.connect()
            try:
                return await service.verify_certificate(
                    certificate_number,
                    ip_address,
                    user_agent
                )
            finally:
                await service.disconnect()

        result = self._run_async(_verify())
        serializer = CertificateVerificationSerializer(result)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Télécharger le PDF"""
        service = CertificatesService()

        async def _get_cert():
            await service.connect()
            try:
                return await service.get_certificate_by_id(pk)
            finally:
                await service.disconnect()

        certificate = self._run_async(_get_cert())

        if not certificate:
            return Response(
                {'error': 'Certificate not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Vérifier l'accès
        if str(certificate['userId']) != str(request.user.id):
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        if not certificate.get('pdfUrl'):
            return Response(
                {'error': 'PDF not yet generated'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Rediriger vers l'URL du PDF
        return HttpResponseRedirect(certificate['pdfUrl'])

    @action(detail=False, methods=['get'])
    def course_certificates(self, request):
        """Lister les certificats d'un cours (instructeur)"""
        course_id = request.query_params.get('courseId')

        if not course_id:
            return Response(
                {'error': 'courseId is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = CertificatesService()

        async def _list():
            await service.connect()
            try:
                return await service.get_course_certificates(course_id)
            finally:
                await service.disconnect()

        certificates = self._run_async(_list())
        serializer = CertificateSerializer(certificates, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Statistiques des certificats"""
        course_id = request.query_params.get('courseId')
        days = int(request.query_params.get('days', 30))

        service = CertificatesService()

        async def _stats():
            await service.connect()
            try:
                return await service.get_certificate_statistics(
                    course_id=course_id,
                    instructor_id=str(request.user.id),
                    days=days
                )
            finally:
                await service.disconnect()

        stats = self._run_async(_stats())
        serializer = CertificateStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def top_courses(self, request):
        """Cours avec le plus de certificats"""
        limit = int(request.query_params.get('limit', 10))

        service = CertificatesService()

        async def _top():
            await service.connect()
            try:
                return await service.get_top_certified_courses(limit)
            finally:
                await service.disconnect()

        top_courses = self._run_async(_top())
        return Response(top_courses)

    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Révoquer un certificat"""
        reason = request.data.get('reason')

        service = CertificatesService()

        async def _revoke():
            await service.connect()
            try:
                return await service.revoke_certificate(pk, reason)
            finally:
                await service.disconnect()

        certificate = self._run_async(_revoke())
        serializer = CertificateSerializer(certificate)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        """Renouveler un certificat"""
        new_expiry = request.data.get('expiresAt')

        if new_expiry:
            new_expiry = datetime.fromisoformat(new_expiry)

        service = CertificatesService()

        async def _renew():
            await service.connect()
            try:
                return await service.renew_certificate(pk, new_expiry)
            finally:
                await service.disconnect()

        certificate = self._run_async(_renew())
        serializer = CertificateSerializer(certificate)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Créer plusieurs certificats en batch"""
        serializer = BulkCertificateCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        service = CertificatesService()

        async def _bulk():
            await service.connect()
            try:
                return await service.bulk_generate_certificates(
                    serializer.validated_data['certificates']
                )
            finally:
                await service.disconnect()

        results = self._run_async(_bulk())
        return Response(results)


class CertificateTemplatesViewSet(viewsets.ViewSet):
    """ViewSet pour les templates"""

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'default']:
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminOrInstructor()]

    def _run_async(self, coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def list(self, request):
        """Lister les templates"""
        active_only = request.query_params.get('activeOnly', 'true') == 'true'

        service = CertificatesService()

        async def _list():
            await service.connect()
            try:
                return await service.list_templates(active_only)
            finally:
                await service.disconnect()

        templates = self._run_async(_list())
        serializer = CertificateTemplateSerializer(templates, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Créer un template"""
        serializer = CertificateTemplateCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        service = CertificatesService()

        async def _create():
            await service.connect()
            try:
                return await service.create_template(serializer.validated_data)
            finally:
                await service.disconnect()

        template = self._run_async(_create())
        response_serializer = CertificateTemplateSerializer(template)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Récupérer un template"""
        service = CertificatesService()

        async def _retrieve():
            await service.connect()
            try:
                return await service.get_template(pk)
            finally:
                await service.disconnect()

        template = self._run_async(_retrieve())

        if not template:
            return Response(
                {'error': 'Template not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CertificateTemplateSerializer(template)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """Mettre à jour un template"""
        service = CertificatesService()

        async def _update():
            await service.connect()
            try:
                return await service.update_template(pk, request.data)
            finally:
                await service.disconnect()

        template = self._run_async(_update())
        serializer = CertificateTemplateSerializer(template)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """Supprimer un template"""
        service = CertificatesService()

        async def _delete():
            await service.connect()
            try:
                return await service.delete_template(pk)
            except ValueError as e:
                return {'error': str(e)}
            finally:
                await service.disconnect()

        result = self._run_async(_delete())

        if isinstance(result, dict) and 'error' in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def default(self, request):
        """Récupérer le template par défaut"""
        service = CertificatesService()

        async def _default():
            await service.connect()
            try:
                return await service.get_default_template()
            finally:
                await service.disconnect()

        template = self._run_async(_default())

        if not template:
            return Response(
                {'error': 'No default template found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CertificateTemplateSerializer(template)
        return Response(serializer.data)
