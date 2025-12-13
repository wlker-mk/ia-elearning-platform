import os
import aiofiles
from django.conf import settings
from .base import BaseStorageProvider
from typing import BinaryIO, Dict, Any

class LocalStorageProvider(BaseStorageProvider):
    """Provider pour stockage local (développement)"""
    
    def __init__(self):
        self.base_path = settings.MEDIA_ROOT
        os.makedirs(self.base_path, exist_ok=True)
    
    async def upload_file(
        self,
        file: BinaryIO,
        key: str,
        content_type: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Upload fichier localement"""
        file_path = os.path.join(self.base_path, key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = file.read() if hasattr(file, 'read') else file
            await f.write(content)
        
        return f"{settings.MEDIA_URL}{key}"
    
    async def download_file(self, key: str) -> bytes:
        """Télécharge fichier local"""
        file_path = os.path.join(self.base_path, key)
        async with aiofiles.open(file_path, 'rb') as f:
            return await f.read()
    
    async def delete_file(self, key: str) -> bool:
        """Supprime fichier local"""
        file_path = os.path.join(self.base_path, key)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    
    async def get_file_url(self, key: str, expires_in: int = 3600) -> str:
        """Retourne l'URL du fichier local"""
        return f"{settings.MEDIA_URL}{key}"
    
    async def file_exists(self, key: str) -> bool:
        """Vérifie existence du fichier"""
        file_path = os.path.join(self.base_path, key)
        return os.path.exists(file_path)