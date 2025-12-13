from django.db import models
import uuid

class UploadSession(models.Model):
    """Modèle Django pour tracking uploads multipart"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=255)
    filename = models.CharField(max_length=500)
    total_size = models.BigIntegerField()
    uploaded_size = models.BigIntegerField(default=0)
    status = models.CharField(max_length=20, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'upload_sessions'
        indexes = [
            models.Index(fields=['user_id', 'status']),
        ]