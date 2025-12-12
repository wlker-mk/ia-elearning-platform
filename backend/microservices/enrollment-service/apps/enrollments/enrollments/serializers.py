from rest_framework import serializers
from datetime import datetime


class EnrollmentCreateSerializer(serializers.Serializer):
    courseId = serializers.CharField(required=True)
    purchasePrice = serializers.FloatField(required=False, allow_null=True)
    paymentId = serializers.CharField(required=False, allow_null=True)
    expiresAt = serializers.DateTimeField(required=False, allow_null=True)


class EnrollmentUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=['ACTIVE', 'COMPLETED', 'SUSPENDED', 'EXPIRED', 'CANCELLED', 'IN_PROGRESS', 'PAUSED'],
        required=False
    )
    expiresAt = serializers.DateTimeField(required=False, allow_null=True)


class EnrollmentSerializer(serializers.Serializer):
    id = serializers.CharField()
    studentId = serializers.CharField()
    courseId = serializers.CharField()
    status = serializers.CharField()
    progress = serializers.FloatField()
    isCompleted = serializers.BooleanField()
    completedAt = serializers.DateTimeField(allow_null=True)
    certificateIssued = serializers.BooleanField()
    certificateId = serializers.CharField(allow_null=True)
    totalTimeSpent = serializers.IntegerField()
    lastAccessedAt = serializers.DateTimeField(allow_null=True)
    purchasePrice = serializers.FloatField(allow_null=True)
    paymentId = serializers.CharField(allow_null=True)
    enrolledAt = serializers.DateTimeField()
    expiresAt = serializers.DateTimeField(allow_null=True)
    createdAt = serializers.DateTimeField()
    updatedAt = serializers.DateTimeField()


class EnrollmentDetailSerializer(EnrollmentSerializer):
    courseDetails = serializers.DictField(required=False)
    studentDetails = serializers.DictField(required=False)
    certificateDetails = serializers.DictField(required=False, allow_null=True)
    progressStats = serializers.DictField(required=False)


class EnrollmentStatsSerializer(serializers.Serializer):
    totalEnrollments = serializers.IntegerField()
    activeEnrollments = serializers.IntegerField()
    completedEnrollments = serializers.IntegerField()
    totalTimeSpent = serializers.IntegerField()
    averageProgress = serializers.FloatField()
    certificatesEarned = serializers.IntegerField()