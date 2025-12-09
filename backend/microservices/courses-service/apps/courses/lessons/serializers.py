from rest_framework import serializers

class LessonContentSerializer(serializers.Serializer):
    """Serializer pour le contenu détaillé d'une leçon"""
    id = serializers.UUIDField(read_only=True)
    sectionId = serializers.UUIDField()
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    content = serializers.CharField(required=False, allow_blank=True)
    order = serializers.IntegerField()
    videoUrl = serializers.URLField(required=False, allow_blank=True)
    videoDuration = serializers.IntegerField(required=False, allow_null=True)
    isFree = serializers.BooleanField(default=False)
    createdAt = serializers.DateTimeField(read_only=True)
    updatedAt = serializers.DateTimeField(read_only=True)

class LessonListSerializer(serializers.Serializer):
    """Serializer léger pour la liste des leçons"""
    id = serializers.UUIDField(read_only=True)
    title = serializers.CharField(max_length=200)
    order = serializers.IntegerField()
    videoDuration = serializers.IntegerField(required=False, allow_null=True)
    isFree = serializers.BooleanField()

class LessonCreateSerializer(serializers.Serializer):
    """Serializer pour créer une leçon"""
    sectionId = serializers.UUIDField()
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    content = serializers.CharField(required=False, allow_blank=True)
    order = serializers.IntegerField()
    videoUrl = serializers.URLField(required=False, allow_blank=True)
    videoDuration = serializers.IntegerField(required=False, allow_null=True)
    isFree = serializers.BooleanField(default=False)

class LessonUpdateSerializer(serializers.Serializer):
    """Serializer pour mettre à jour une leçon"""
    title = serializers.CharField(max_length=200, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    content = serializers.CharField(required=False, allow_blank=True)
    order = serializers.IntegerField(required=False)
    videoUrl = serializers.URLField(required=False, allow_blank=True)
    videoDuration = serializers.IntegerField(required=False, allow_null=True)
    isFree = serializers.BooleanField(required=False)

class ResourceSerializer(serializers.Serializer):
    """Serializer pour les ressources de leçon"""
    id = serializers.UUIDField(read_only=True)
    lessonId = serializers.UUIDField()
    title = serializers.CharField(max_length=200)
    type = serializers.CharField(max_length=50)
    url = serializers.URLField()
    fileSize = serializers.IntegerField(required=False, allow_null=True)
    isDownloadable = serializers.BooleanField(default=True)
    downloadCount = serializers.IntegerField(read_only=True)
    createdAt = serializers.DateTimeField(read_only=True)
    updatedAt = serializers.DateTimeField(read_only=True)

class ResourceCreateSerializer(serializers.Serializer):
    """Serializer pour créer une ressource"""
    lessonId = serializers.UUIDField()
    title = serializers.CharField(max_length=200)
    type = serializers.ChoiceField(choices=[
        'PDF', 'VIDEO', 'AUDIO', 'ZIP', 
        'DOCUMENT', 'CODE', 'LINK', 'IMAGE'
    ])
    url = serializers.URLField()
    fileSize = serializers.IntegerField(required=False, allow_null=True)
    isDownloadable = serializers.BooleanField(default=True)

class LessonWithResourcesSerializer(LessonContentSerializer):
    """Serializer complet avec ressources"""
    resources = ResourceSerializer(many=True, read_only=True)

class BulkLessonOrderSerializer(serializers.Serializer):
    """Serializer pour réorganiser plusieurs leçons"""
    lessons = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField())
    )
    # Format attendu: [{"id": "uuid", "order": 1}, ...]