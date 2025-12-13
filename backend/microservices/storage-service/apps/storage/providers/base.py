from abc import ABC, abstractmethod
from typing import BinaryIO, Dict, Any

class BaseStorageProvider(ABC):
    """Interface commune pour tous les providers de storage"""
    
    @abstractmethod
    async def upload_file(
        self,
        file: BinaryIO,
        key: str,
        content_type: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Upload un fichier et retourne l'URL"""
        pass
    
    @abstractmethod
    async def download_file(self, key: str) -> bytes:
        """Télécharge un fichier"""
        pass
    
    @abstractmethod
    async def delete_file(self, key: str) -> bool:
        """Supprime un fichier"""
        pass
    
    @abstractmethod
    async def get_file_url(self, key: str, expires_in: int = 3600) -> str:
        """Génère une URL signée"""
        pass
    
    @abstractmethod
    async def file_exists(self, key: str) -> bool:
        """Vérifie si un fichier existe"""
        pass