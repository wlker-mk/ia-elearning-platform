from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
import uuid
import asyncio
from asgiref.sync import async_to_sync

from .serializers import (
    FileSerializer, UploadSerializer, MediaAssetSerializer,
    FileUploadRequestSerializer, InitiateUploadRequestSerializer
)
from .services import StorageService
from .providers.local_storage import LocalStorageProvider
from .providers.s3_storage import S3StorageProvider

def get_storage_provider():
    """Factory pour provider de storage"""
    provider = settings.STORAGE_PROVIDER
    if provider == 'AWS_S3':
        return S3StorageProvider()
    else:
        return LocalStorageProvider()


class FileViewSet(viewsets.ViewSet):
    """ViewSet pour gestion des fichiers"""
    parser_classes = (MultiPartParser, FormParser)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = StorageService()
        self.storage_provider = get_storage_provider()
    
    def list(self, request):
        """Liste les fichiers de l'utilisateur"""
        async def _list():
            await self.service.connect()
            try:
                user_id = request.user_id if hasattr(request, 'user_id') else 'anonymous'
                file_type = request.query_params.get('fileType')
                skip = int(request.query_params.get('skip', 0))
                limit = int(request.query_params.get('limit', 20))
                
                files = await self.service.list_files(
                    user_id=user_id,
                    file_type=file_type,
                    skip=skip,
                    limit=limit
                )
                return files
            finally:
                await self.service.disconnect()
        
        files = async_to_sync(_list)()
        serializer = FileSerializer(files, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        """Upload un fichier direct"""
        serializer = FileUploadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        async def _create():
            await self.service.connect()
            try:
                uploaded_file = serializer.validated_data['file']
                user_id = request.user_id if hasattr(request, 'user_id') else 'anonymous'
                
                # Génère storage key unique
                storage_key = self.service.generate_storage_key(user_id, uploaded_file.name)
                
                # Upload vers le provider
                url = await self.storage_provider.upload_file(
                    file=uploaded_file,
                    key=storage_key,
                    content_type=uploaded_file.content_type
                )
                
                # Détecte le type de fichier
                file_type = self.service.detect_file_type(uploaded_file.content_type)
                
                # Crée l'enregistrement
                file_data = {
                    'filename': storage_key.split('/')[-1],
                    'original_name': uploaded_file.name,
                    'mime_type': uploaded_file.content_type,
                    'file_type': file_type,
                    'file_size': uploaded_file.size,
                    'storage_key': storage_key,
                    'url': url,
                    'is_public': serializer.validated_data.get('isPublic', False),
                    'related_entity': serializer.validated_data.get('relatedEntity'),
                    'related_entity_id': serializer.validated_data.get('relatedEntityId'),
                }
                file = await self.service.create_file(user_id, file_data)
                return file
            finally:
                await self.service.disconnect()
        
        file = async_to_sync(_create)()
        return Response(FileSerializer(file).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Récupère un fichier par ID"""
        async def _retrieve():
            await self.service.connect()
            try:
                file = await self.service.get_file(pk)
                if file:
                    await self.service.increment_view_count(pk)
                return file
            finally:
                await self.service.disconnect()
        
        file = async_to_sync(_retrieve)()
        if not file:
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(FileSerializer(file).data)

    def destroy(self, request, pk=None):
        """Supprime un fichier"""
        async def _destroy():
            await self.service.connect()
            try:
                deleted = await self.service.delete_file(pk)
                return deleted
            finally:
                await self.service.disconnect()
        
        deleted = async_to_sync(_destroy)()
        if not deleted:
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Génère URL de téléchargement"""
        async def _download():
            await self.service.connect()
            try:
                file = await self.service.get_file(pk)
                if not file:
                    return None
                
                await self.service.increment_download_count(pk)
                download_url = await self.storage_provider.get_file_url(file['storageKey'])
                return download_url
            finally:
                await self.service.disconnect()
        
        url = async_to_sync(_download)()
        if not url:
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'downloadUrl': url})


class UploadViewSet(viewsets.ViewSet):
    """ViewSet pour gestion des uploads multipart"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = StorageService()

    @action(detail=False, methods=['post'])
    def initiate(self, request):
        """Initie un upload multipart"""
        serializer = InitiateUploadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        async def _initiate():
            await self.service.connect()
            try:
                user_id = request.user_id if hasattr(request, 'user_id') else 'anonymous'
                session_id = str(uuid.uuid4())
                
                upload = await self.service.create_upload(
                    user_id=user_id,
                    session_id=session_id,
                    filename=serializer.validated_data['filename'],
                    file_size=serializer.validated_data['fileSize'],
                    mime_type=serializer.validated_data['mimeType']
                )
                return upload
            finally:
                await self.service.disconnect()
        
        upload = async_to_sync(_initiate)()
        return Response(UploadSerializer(upload).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complète un upload"""
        file_id = request.data.get('fileId')
        if not file_id:
            return Response({'error': 'fileId required'}, status=status.HTTP_400_BAD_REQUEST)
        
        async def _complete():
            await self.service.connect()
            try:
                upload = await self.service.complete_upload(pk, file_id)
                return upload
            finally:
                await self.service.disconnect()
        
        upload = async_to_sync(_complete)()
        return Response(UploadSerializer(upload).data)
