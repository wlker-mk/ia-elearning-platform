from rest_framework import serializers


class ProgressCreateUpdateSerializer(serializers.Serializer):
    lessonId = serializers.CharField(required=True)
    courseId = serializers.CharField(required=True)
    percentage = serializers.FloatField(required=False, min_value=0, max_value=100)
    timeSpent = serializers.IntegerField(required=False, min_value=0)
    lastPosition = serializers.IntegerField(required=False, min_value=0)
    watchedDuration = serializers.IntegerField(required=False, min_value=0)
    quizScore = serializers.FloatField(required=False, min_value=0, max_value=100)
    isCompleted = serializers.BooleanField(required=False)


class ProgressSerializer(serializers.Serializer):
    id = serializers.CharField()
    studentId = serializers.CharField()
    lessonId = serializers.CharField()
    courseId = serializers.CharField()
    enrollmentId = serializers.CharField()
    isCompleted = serializers.BooleanField()
    percentage = serializers.FloatField()
    timeSpent = serializers.IntegerField()
    lastPosition = serializers.IntegerField(allow_null=True)
    watchedDuration = serializers.IntegerField()
    quizScore = serializers.FloatField(allow_null=True)
    quizAttempts = serializers.IntegerField()
    notesCount = serializers.IntegerField()
    questionsAsked = serializers.IntegerField()
    completedAt = serializers.DateTimeField(allow_null=True)
    firstAccessedAt = serializers.DateTimeField()
    lastAccessedAt = serializers.DateTimeField()
    createdAt = serializers.DateTimeField()
    updatedAt = serializers.DateTimeField()


class StudySessionCreateSerializer(serializers.Serializer):
    courseId = serializers.CharField(required=True)
    lessonId = serializers.CharField(required=False, allow_null=True)
    deviceInfo = serializers.CharField(required=False, allow_null=True)


class StudySessionSerializer(serializers.Serializer):
    id = serializers.CharField()
    studentId = serializers.CharField()
    courseId = serializers.CharField()
    lessonId = serializers.CharField(allow_null=True)
    enrollmentId = serializers.CharField()
    startTime = serializers.DateTimeField()
    endTime = serializers.DateTimeField(allow_null=True)
    duration = serializers.IntegerField()
    isActive = serializers.BooleanField()
    deviceInfo = serializers.CharField(allow_null=True)
    ipAddress = serializers.CharField(allow_null=True)
    createdAt = serializers.DateTimeField()
    updatedAt = serializers.DateTimeField()


class CourseProgressSerializer(serializers.Serializer):
    courseId = serializers.CharField()
    totalLessons = serializers.IntegerField()
    completedLessons = serializers.IntegerField()
    overallProgress = serializers.FloatField()
    totalTimeSpent = serializers.IntegerField()
    lastAccessedAt = serializers.DateTimeField(allow_null=True)
    lessons = ProgressSerializer(many=True)


class ProgressStatsSerializer(serializers.Serializer):
    totalCoursesInProgress = serializers.IntegerField()
    totalLessonsCompleted = serializers.IntegerField()
    totalTimeSpent = serializers.IntegerField()
    averageProgress = serializers.FloatField()
    currentStreak = serializers.IntegerField()
    longestStreak = serializers.IntegerField()