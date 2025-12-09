from rest_framework import serializers

class TagSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=50)
    slug = serializers.SlugField(read_only=True)
    usageCount = serializers.IntegerField(read_only=True)
    createdAt = serializers.DateTimeField(read_only=True)
    updatedAt = serializers.DateTimeField(read_only=True)

class CategorySerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=100)
    slug = serializers.SlugField(read_only=True)
    description = serializers.CharField(required=False, allow_blank=True)
    imageUrl = serializers.URLField(required=False, allow_blank=True)
    isActive = serializers.BooleanField(default=True)
    createdAt = serializers.DateTimeField(read_only=True)
    updatedAt = serializers.DateTimeField(read_only=True)

class ResourceSerializer(serializers.Serializer):
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

class LessonSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    sectionId = serializers.UUIDField()
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    content = serializers.CharField(required=False, allow_blank=True)
    order = serializers.IntegerField()
    videoUrl = serializers.URLField(required=False, allow_blank=True)
    videoDuration = serializers.IntegerField(required=False, allow_null=True)
    isFree = serializers.BooleanField(default=False)
    resources = ResourceSerializer(many=True, read_only=True)
    createdAt = serializers.DateTimeField(read_only=True)
    updatedAt = serializers.DateTimeField(read_only=True)

class SectionSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    courseId = serializers.UUIDField()
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    order = serializers.IntegerField()
    duration = serializers.IntegerField(read_only=True)
    lessons = LessonSerializer(many=True, read_only=True)
    createdAt = serializers.DateTimeField(read_only=True)
    updatedAt = serializers.DateTimeField(read_only=True)

class CourseListSerializer(serializers.Serializer):
    """Serializer léger pour la liste des cours"""
    id = serializers.UUIDField(read_only=True)
    slug = serializers.SlugField(read_only=True)
    title = serializers.CharField(max_length=200)
    subtitle = serializers.CharField(max_length=300, required=False, allow_blank=True)
    instructorId = serializers.UUIDField()
    categoryId = serializers.UUIDField()
    language = serializers.CharField(default='ENGLISH')
    difficulty = serializers.ChoiceField(choices=[
        'BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT', 'ALL_LEVELS'
    ])
    type = serializers.ChoiceField(choices=[
        'VIDEO_COURSE', 'TEXT_BASED', 'MIXED', 'LIVE_CLASS', 
        'WORKSHOP', 'BOOTCAMP', 'CERTIFICATION_PREP'
    ])
    price = serializers.FloatField()
    isFree = serializers.BooleanField(default=False)
    thumbnailUrl = serializers.URLField(required=False, allow_blank=True)
    estimatedDuration = serializers.IntegerField()
    enrollmentCount = serializers.IntegerField(read_only=True)
    completionCount = serializers.IntegerField(read_only=True)
    rating = serializers.FloatField(read_only=True)
    reviewCount = serializers.IntegerField(read_only=True)
    publishedAt = serializers.DateTimeField(read_only=True, allow_null=True)
    createdAt = serializers.DateTimeField(read_only=True)
    updatedAt = serializers.DateTimeField(read_only=True)

class CourseDetailSerializer(CourseListSerializer):
    """Serializer détaillé avec sections et leçons"""
    description = serializers.CharField()
    sections = SectionSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

class CourseCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    subtitle = serializers.CharField(max_length=300, required=False, allow_blank=True)
    description = serializers.CharField()
    categoryId = serializers.UUIDField()
    language = serializers.CharField(default='ENGLISH')
    difficulty = serializers.ChoiceField(choices=[
        'BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT', 'ALL_LEVELS'
    ])
    type = serializers.ChoiceField(choices=[
        'VIDEO_COURSE', 'TEXT_BASED', 'MIXED', 'LIVE_CLASS', 
        'WORKSHOP', 'BOOTCAMP', 'CERTIFICATION_PREP'
    ])
    price = serializers.FloatField()
    isFree = serializers.BooleanField(default=False)
    thumbnailUrl = serializers.URLField(required=False, allow_blank=True)
    estimatedDuration = serializers.IntegerField()
    tagIds = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True
    )

class CourseUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200, required=False)
    subtitle = serializers.CharField(max_length=300, required=False, allow_blank=True)
    description = serializers.CharField(required=False)
    categoryId = serializers.UUIDField(required=False)
    language = serializers.CharField(required=False)
    difficulty = serializers.ChoiceField(
        choices=['BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT', 'ALL_LEVELS'],
        required=False
    )
    type = serializers.ChoiceField(
        choices=['VIDEO_COURSE', 'TEXT_BASED', 'MIXED', 'LIVE_CLASS', 
                 'WORKSHOP', 'BOOTCAMP', 'CERTIFICATION_PREP'],
        required=False
    )
    price = serializers.FloatField(required=False)
    isFree = serializers.BooleanField(required=False)
    thumbnailUrl = serializers.URLField(required=False, allow_blank=True)
    estimatedDuration = serializers.IntegerField(required=False)

class SectionCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    order = serializers.IntegerField()

class LessonCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    content = serializers.CharField(required=False, allow_blank=True)
    order = serializers.IntegerField()
    videoUrl = serializers.URLField(required=False, allow_blank=True)
    videoDuration = serializers.IntegerField(required=False, allow_null=True)
    isFree = serializers.BooleanField(default=False)

class ResourceCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    type = serializers.CharField(max_length=50)
    url = serializers.URLField()
    fileSize = serializers.IntegerField(required=False, allow_null=True)
    isDownloadable = serializers.BooleanField(default=True)

class WishlistSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    studentId = serializers.UUIDField()
    courseId = serializers.UUIDField()
    addedAt = serializers.DateTimeField(read_only=True)
    course = CourseListSerializer(read_only=True)

class CourseStatsSerializer(serializers.Serializer):
    """Statistiques d'un cours pour l'instructeur"""
    courseId = serializers.UUIDField()
    enrollmentCount = serializers.IntegerField()
    completionCount = serializers.IntegerField()
    averageRating = serializers.FloatField()
    reviewCount = serializers.IntegerField()
    totalRevenue = serializers.FloatField()
    completionRate = serializers.FloatField()