from rest_framework import serializers

class CertificateSerializer(serializers.Serializer):
    """Serializer pour un certificat"""
    id = serializers.UUIDField(read_only=True)
    userId = serializers.UUIDField()
    courseId = serializers.UUIDField()
    certificateNumber = serializers.CharField(read_only=True)
    issuedAt = serializers.DateTimeField(read_only=True)
    expiresAt = serializers.DateTimeField(allow_null=True, required=False)
    pdfUrl = serializers.URLField(read_only=True, allow_null=True)
    verificationUrl = serializers.URLField(read_only=True)
    grade = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    completionDate = serializers.DateTimeField()
    metadata = serializers.JSONField(required=False, allow_null=True)
    createdAt = serializers.DateTimeField(read_only=True)
    updatedAt = serializers.DateTimeField(read_only=True)

class CertificateCreateSerializer(serializers.Serializer):
    """Serializer pour créer un certificat"""
    userId = serializers.UUIDField()
    courseId = serializers.UUIDField()
    completionDate = serializers.DateTimeField()
    grade = serializers.CharField(required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False)

class CertificateVerificationSerializer(serializers.Serializer):
    """Serializer pour la vérification d'un certificat"""
    certificateNumber = serializers.CharField()
    isValid = serializers.BooleanField()
    certificate = CertificateSerializer(required=False, allow_null=True)
    message = serializers.CharField(required=False)
    verifiedAt = serializers.DateTimeField(read_only=True)

class CertificateTemplateSerializer(serializers.Serializer):
    """Serializer pour un template de certificat"""
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    templateHtml = serializers.CharField()
    templateCss = serializers.CharField(required=False, allow_blank=True)
    isDefault = serializers.BooleanField(default=False)
    isActive = serializers.BooleanField(default=True)
    previewUrl = serializers.URLField(required=False, allow_blank=True)
    createdAt = serializers.DateTimeField(read_only=True)
    updatedAt = serializers.DateTimeField(read_only=True)

class CertificateTemplateCreateSerializer(serializers.Serializer):
    """Serializer pour créer un template"""
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    templateHtml = serializers.CharField()
    templateCss = serializers.CharField(required=False, allow_blank=True)
    isDefault = serializers.BooleanField(default=False)
    isActive = serializers.BooleanField(default=True)

class CertificateStatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques de certificats"""
    totalIssued = serializers.IntegerField()
    totalVerifications = serializers.IntegerField()
    issuedThisMonth = serializers.IntegerField()
    issuedThisWeek = serializers.IntegerField()
    issuedToday = serializers.IntegerField()
    averageTimeToComplete = serializers.IntegerField()  # en jours
    topCourses = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )

class BulkCertificateCreateSerializer(serializers.Serializer):
    """Serializer pour créer plusieurs certificats en batch"""
    certificates = serializers.ListField(
        child=serializers.DictField()
    )
    # Format: [{"userId": "uuid", "courseId": "uuid", "completionDate": "date"}, ...]

class CertificateWithCourseSerializer(CertificateSerializer):
    """Serializer avec informations du cours"""
    course = serializers.DictField(read_only=True)
    user = serializers.DictField(read_only=True)