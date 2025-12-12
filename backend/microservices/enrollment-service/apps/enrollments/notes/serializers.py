from rest_framework import serializers


class NoteCreateSerializer(serializers.Serializer):
    courseId = serializers.CharField(required=True)
    lessonId = serializers.CharField(required=True)
    type = serializers.ChoiceField(
        choices=['TEXT', 'HIGHLIGHT', 'QUESTION'],
        default='TEXT'
    )
    content = serializers.CharField(required=True, max_length=5000)
    highlight = serializers.CharField(required=False, allow_null=True, max_length=1000)
    timestamp = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    pageNumber = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    isPrivate = serializers.BooleanField(default=True)
    color = serializers.CharField(required=False, allow_null=True, max_length=20)


class NoteUpdateSerializer(serializers.Serializer):
    content = serializers.CharField(required=False, max_length=5000)
    highlight = serializers.CharField(required=False, allow_null=True, max_length=1000)
    isPrivate = serializers.BooleanField(required=False)
    color = serializers.CharField(required=False, allow_null=True, max_length=20)


class NoteSerializer(serializers.Serializer):
    id = serializers.CharField()
    studentId = serializers.CharField()
    courseId = serializers.CharField()
    lessonId = serializers.CharField()
    enrollmentId = serializers.CharField()
    type = serializers.CharField()
    content = serializers.CharField()
    highlight = serializers.CharField(allow_null=True)
    timestamp = serializers.IntegerField(allow_null=True)
    pageNumber = serializers.IntegerField(allow_null=True)
    isPrivate = serializers.BooleanField()
    color = serializers.CharField(allow_null=True)
    createdAt = serializers.DateTimeField()
    updatedAt = serializers.DateTimeField()


class BookmarkCreateSerializer(serializers.Serializer):
    courseId = serializers.CharField(required=True)
    lessonId = serializers.CharField(required=True)
    type = serializers.ChoiceField(
        choices=['LESSON', 'TIMESTAMP', 'RESOURCE'],
        default='LESSON'
    )
    title = serializers.CharField(required=True, max_length=200)
    description = serializers.CharField(required=False, allow_null=True, max_length=500)
    timestamp = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    url = serializers.URLField(required=False, allow_null=True)


class BookmarkSerializer(serializers.Serializer):
    id = serializers.CharField()
    studentId = serializers.CharField()
    courseId = serializers.CharField()
    lessonId = serializers.CharField()
    enrollmentId = serializers.CharField()
    type = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    timestamp = serializers.IntegerField(allow_null=True)
    url = serializers.CharField(allow_null=True)
    createdAt = serializers.DateTimeField()
    updatedAt = serializers.DateTimeField()


class CertificateSerializer(serializers.Serializer):
    id = serializers.CharField()
    studentId = serializers.CharField()
    courseId = serializers.CharField()
    enrollmentId = serializers.CharField()
    certificateNumber = serializers.CharField()
    verificationCode = serializers.CharField()
    studentName = serializers.CharField()
    studentEmail = serializers.CharField()
    courseTitle = serializers.CharField()
    completionDate = serializers.DateTimeField()
    issueDate = serializers.DateTimeField()
    score = serializers.FloatField(allow_null=True)
    grade = serializers.CharField(allow_null=True)
    certificateUrl = serializers.CharField(allow_null=True)
    isValid = serializers.BooleanField()
    revokedAt = serializers.DateTimeField(allow_null=True)
    createdAt = serializers.DateTimeField()
    updatedAt = serializers.DateTimeField()


class CertificateVerificationSerializer(serializers.Serializer):
    isValid = serializers.BooleanField()
    certificate = CertificateSerializer(allow_null=True)
    message = serializers.CharField()