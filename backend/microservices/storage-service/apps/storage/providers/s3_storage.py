import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from .base import BaseStorageProvider
from typing import BinaryIO, Dict, Any
import logging

logger = logging.getLogger(__name__)

class S3StorageProvider(BaseStorageProvider):
    """Provider pour AWS S3"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket = settings.AWS_STORAGE_BUCKET_NAME
    
    async def upload_file(
        self,
        file: BinaryIO,
        key: str,
        content_type: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Upload vers S3"""
        try:
            extra_args = {
                'ContentType': content_type
            }
            if metadata:
                extra_args['Metadata'] = metadata
            
            content = file.read() if hasattr(file, 'read') else file
            
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=content,
                **extra_args
            )
            
            return f"https://{self.bucket}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            raise
    
    async def download_file(self, key: str) -> bytes:
        """Télécharge depuis S3"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            return response['Body'].read()
        except ClientError as e:
            logger.error(f"S3 download error: {e}")
            raise
    
    async def delete_file(self, key: str) -> bool:
        """Supprime depuis S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as e:
            logger.error(f"S3 delete error: {e}")
            return False
    
    async def get_file_url(self, key: str, expires_in: int = 3600) -> str:
        """Génère URL signée S3"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': key},
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            logger.error(f"S3 presigned URL error: {e}")
            raise
    
    async def file_exists(self, key: str) -> bool:
        """Vérifie existence dans S3"""
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError:
            return False