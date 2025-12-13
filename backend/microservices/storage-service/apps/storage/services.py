from typing import List, Optional, Dict, Any
from prisma import Prisma
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
import uuid
import os
import hashlib
from datetime import datetime, timedelta, timezone

class StorageService:
    def __init__(self):
        self.db = Prisma()
        self.provider = settings.STORAGE_PROVIDER
    
    async def connect(self):
        if not self.db.is_connected():
            await self.db.connect()
    
    async def disconnect(self):
        if self.db.is_connected():
            await self.db.disconnect()
    
    async def create_file(
        self,
        user_id: str,
        file_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Crée un enregistrement de fichier dans la DB"""
        file = await self.db.file.create(
            data={
                'userId': user_id,
                'filename': file_data['filename'],
                'originalName': file_data['original_name'],
                'mimeType': file_data['mime_type'],
                'fileType': file_data['file_type'],
                'fileSize': file_data['file_size'],
                'provider': self.provider,
                'storageKey': file_data['storage_key'],
                'bucket': file_data.get('bucket'),
                'url': file_data['url'],
                'cdnUrl': file_data.get('cdn_url'),
                'isPublic': file_data.get('is_public', False),
                'relatedEntity': file_data.get('related_entity'),
                'relatedEntityId': file_data.get('related_entity_id'),
            }
        )
        return file.dict()
    
    async def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un fichier par ID"""
        file = await self.db.file.find_unique(where={'id': file_id})
        return file.dict() if file else None
    
    async def list_files(
        self,
        user_id: Optional[str] = None,
        file_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Liste les fichiers avec filtres"""
        where = {}
        if user_id:
            where['userId'] = user_id
        if file_type:
            where['fileType'] = file_type
        
        files = await self.db.file.find_many(
            where=where,
            skip=skip,
            take=limit,
            order={'createdAt': 'desc'}
        )
        return [f.dict() for f in files]
    
    async def delete_file(self, file_id: str) -> bool:
        """Supprime un fichier (soft delete)"""
        file = await self.db.file.update(
            where={'id': file_id},
            data={'deletedAt': datetime.now(timezone.utc)}
        )
        return bool(file)
    
    async def increment_download_count(self, file_id: str):
        """Incrémente le compteur de téléchargements"""
        await self.db.file.update(
            where={'id': file_id},
            data={'downloadCount': {'increment': 1}}
        )
    
    async def increment_view_count(self, file_id: str):
        """Incrémente le compteur de vues"""
        await self.db.file.update(
            where={'id': file_id},
            data={'viewCount': {'increment': 1}}
        )
    
    # Upload Management
    async def create_upload(
        self,
        user_id: str,
        session_id: str,
        filename: str,
        file_size: int,
        mime_type: str
    ) -> Dict[str, Any]:
        """Crée une session d'upload"""
        upload = await self.db.upload.create(
            data={
                'userId': user_id,
                'sessionId': session_id,
                'filename': filename,
                'fileSize': file_size,
                'mimeType': mime_type,
                'status': 'PENDING'
            }
        )
        return upload.dict()
    
    async def update_upload_progress(
        self,
        session_id: str,
        bytes_uploaded: int,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Met à jour la progression d'un upload"""
        upload = await self.db.upload.find_unique(where={'sessionId': session_id})
        if not upload:
            raise ValueError(f"Upload session {session_id} not found")
        
        progress = (bytes_uploaded / upload.fileSize) * 100
        
        update_data = {
            'bytesUploaded': bytes_uploaded,
            'progress': progress
        }
        
        if status:
            update_data['status'] = status
            if status == 'COMPLETED':
                update_data['completedAt'] = datetime.now(timezone.utc)
        
        updated = await self.db.upload.update(
            where={'sessionId': session_id},
            data=update_data
        )
        return updated.dict()
    
    async def complete_upload(
        self,
        session_id: str,
        file_id: str
    ) -> Dict[str, Any]:
        """Complète un upload et lie au fichier"""
        upload = await self.db.upload.update(
            where={'sessionId': session_id},
            data={
                'status': 'COMPLETED',
                'fileId': file_id,
                'completedAt': datetime.now(timezone.utc)
            }
        )
        return upload.dict()
    
    # Media Asset Management
    async def create_media_asset(
        self,
        file_id: str,
        original_url: str,
        original_size: int
    ) -> Dict[str, Any]:
        """Crée un asset média pour processing"""
        asset = await self.db.mediaasset.create(
            data={
                'fileId': file_id,
                'originalUrl': original_url,
                'originalSize': original_size,
                'isProcessed': False
            }
        )
        return asset.dict()
    
    async def update_media_asset(
        self,
        file_id: str,
        processed_urls: Dict[str, str]
    ) -> Dict[str, Any]:
        """Met à jour un asset avec les URLs processées"""
        asset = await self.db.mediaasset.update(
            where={'fileId': file_id},
            data={
                **processed_urls,
                'isProcessed': True,
                'processingCompleted': datetime.now(timezone.utc)
            }
        )
        return asset.dict()
    
    def generate_storage_key(self, user_id: str, filename: str) -> str:
        """Génère une clé de storage unique"""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        random_hash = hashlib.md5(f"{user_id}{filename}{timestamp}".encode(), usedforsecurity=False).hexdigest()[:8]
        extension = os.path.splitext(filename)[1]
        return f"uploads/{user_id}/{timestamp}_{random_hash}{extension}"
    
    def detect_file_type(self, mime_type: str) -> str:
        """Détecte le type de fichier depuis le MIME type"""
        if mime_type.startswith('video/'):
            return 'VIDEO'
        elif mime_type.startswith('image/'):
            return 'IMAGE'
        elif mime_type.startswith('audio/'):
            return 'AUDIO'
        elif mime_type in ['application/pdf']:
            return 'DOCUMENT'
        elif mime_type in ['application/zip', 'application/x-rar']:
            return 'ARCHIVE'
        else:
            return 'OTHER'