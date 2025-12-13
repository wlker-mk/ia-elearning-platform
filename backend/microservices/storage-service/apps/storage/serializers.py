from rest_framework import serializers

class FileSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    userId = serializers.CharField(max_length=255)
    filename = serializers.CharField(max_length=500)
    originalName = serializers.CharField(max_length=500)
    mimeType = serializers.CharField(max_length=100)
    fileType = serializers.CharField(max_length=50)
    fileSize = serializers.IntegerField()
    provider = serializers.CharField(max_length=50)
    storageKey = serializers.CharField(max_length=500)
    bucket = serializers.CharField(max_length=200, required=False, allow_null=True)
    url = serializers.URLField()
    cdnUrl = serializers.URLField(required=False, allow_null=True)
    width = serializers.IntegerField(required=False, allow_null=True)
    height = serializers.IntegerField(required=False, allow_null=True)
    duration = serializers.IntegerField(required=False, allow_null=True)
    status = serializers.CharField(max_length=50)
    thumbnailUrl = serializers.URLField(required=False, allow_null=True)
    isPublic = serializers.BooleanField(default=False)
    downloadCount = serializers.IntegerField(read_only=True)
    viewCount = serializers.IntegerField(read_only=True)
    relatedEntity = serializers.CharField(max_length=100, required=False, allow_null=True)
    relatedEntityId = serializers.CharField(max_length=255, required=False, allow_null=True)
    uploadedAt = serializers.DateTimeField(read_only=True)
    createdAt = serializers.DateTimeField(read_only=True)
    updatedAt = serializers.DateTimeField(read_only=True)


class UploadSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    userId = serializers.CharField(max_length=255)
    sessionId = serializers.CharField(max_length=255)
    filename = serializers.CharField(max_length=500)
    fileSize = serializers.IntegerField()
    mimeType = serializers.CharField(max_length=100)
    uploadId = serializers.CharField(max_length=255, required=False, allow_null=True)
    bytesUploaded = serializers.IntegerField(read_only=True)
    progress = serializers.FloatField(read_only=True)
    status = serializers.CharField(max_length=50)
    fileId = serializers.CharField(max_length=255, required=False, allow_null=True)
    errorMessage = serializers.CharField(required=False, allow_null=True)
    startedAt = serializers.DateTimeField(read_only=True)
    completedAt = serializers.DateTimeField(required=False, allow_null=True)


class MediaAssetSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    fileId = serializers.CharField(max_length=255)
    originalUrl = serializers.URLField()
    originalSize = serializers.IntegerField()
    thumbnailUrl = serializers.URLField(required=False, allow_null=True)
    smallUrl = serializers.URLField(required=False, allow_null=True)
    mediumUrl = serializers.URLField(required=False, allow_null=True)
    largeUrl = serializers.URLField(required=False, allow_null=True)
    streamUrl = serializers.URLField(required=False, allow_null=True)
    isProcessed = serializers.BooleanField(default=False)
    createdAt = serializers.DateTimeField(read_only=True)


class FileUploadRequestSerializer(serializers.Serializer):
    file = serializers.FileField()
    fileType = serializers.CharField(max_length=50, required=False)
    isPublic = serializers.BooleanField(default=False)
    relatedEntity = serializers.CharField(max_length=100, required=False)
    relatedEntityId = serializers.CharField(max_length=255, required=False)


class InitiateUploadRequestSerializer(serializers.Serializer):
    filename = serializers.CharField(max_length=500)
    fileSize = serializers.IntegerField()
    mimeType = serializers.CharField(max_length=100)
    chunks = serializers.IntegerField(default=1)