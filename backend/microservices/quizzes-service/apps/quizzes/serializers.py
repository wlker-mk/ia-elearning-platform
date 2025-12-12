from rest_framework import serializers
from datetime import datetime

class BaseSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class QuestionSerializer(BaseSerializer):
    quiz_id = serializers.UUIDField(required=False)
    type = serializers.ChoiceField(choices=[
        'MULTIPLE_CHOICE', 'TRUE_FALSE', 'SHORT_ANSWER', 
        'ESSAY', 'CODING', 'MATCHING', 'FILL_BLANK'
    ])
    question = serializers.CharField()
    order = serializers.IntegerField()
    points = serializers.FloatField(default=1.0)
    options = serializers.JSONField(required=False, allow_null=True)
    correct_answer = serializers.JSONField(required=False, allow_null=True)
    explanation = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class QuizSerializer(BaseSerializer):
    lesson_id = serializers.UUIDField()
    course_id = serializers.UUIDField()
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    duration = serializers.IntegerField(required=False, allow_null=True)
    passing_score = serializers.FloatField(default=70.0)
    max_attempts = serializers.IntegerField(default=3)
    randomize_questions = serializers.BooleanField(default=False)
    questions = QuestionSerializer(many=True, read_only=True)


class QuizCreateSerializer(serializers.Serializer):
    lesson_id = serializers.UUIDField()
    course_id = serializers.UUIDField()
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    duration = serializers.IntegerField(required=False, allow_null=True)
    passing_score = serializers.FloatField(default=70.0)
    max_attempts = serializers.IntegerField(default=3)
    randomize_questions = serializers.BooleanField(default=False)
    questions = QuestionSerializer(many=True, required=False)


class QuizUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    duration = serializers.IntegerField(required=False, allow_null=True)
    passing_score = serializers.FloatField(required=False)
    max_attempts = serializers.IntegerField(required=False)
    randomize_questions = serializers.BooleanField(required=False)


class QuizAttemptSerializer(BaseSerializer):
    quiz_id = serializers.UUIDField()
    student_id = serializers.UUIDField(read_only=True)
    attempt_number = serializers.IntegerField(read_only=True)
    score = serializers.FloatField(read_only=True)
    percentage = serializers.FloatField(read_only=True)
    is_passed = serializers.BooleanField(read_only=True)
    answers = serializers.JSONField()
    started_at = serializers.DateTimeField()
    submitted_at = serializers.DateTimeField(required=False, allow_null=True)
    time_spent = serializers.IntegerField(required=False, allow_null=True)


class QuizAttemptStartSerializer(serializers.Serializer):
    quiz_id = serializers.UUIDField()


class QuizAttemptSubmitSerializer(serializers.Serializer):
    answers = serializers.JSONField()


class ProctoringSessionSerializer(BaseSerializer):
    quiz_attempt_id = serializers.UUIDField()
    webcam_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    screen_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    audio_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    face_detections = serializers.JSONField(required=False, allow_null=True)
    suspicious_activity = serializers.JSONField(required=False, allow_null=True)
    tab_switches = serializers.IntegerField(default=0)
    multiple_faces = serializers.BooleanField(default=False)
    no_face_detected = serializers.BooleanField(default=False)
    copy_paste_detected = serializers.BooleanField(default=False)
    flagged_for_review = serializers.BooleanField(default=False)
    reviewed_by = serializers.UUIDField(required=False, allow_null=True)
    reviewed_at = serializers.DateTimeField(required=False, allow_null=True)
    review_notes = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    started_at = serializers.DateTimeField(read_only=True)
    ended_at = serializers.DateTimeField(required=False, allow_null=True)


class ProctoringEventSerializer(serializers.Serializer):
    quiz_attempt_id = serializers.UUIDField()
    event_type = serializers.ChoiceField(choices=[
        'tab_switch', 'multiple_faces', 'no_face', 'copy_paste'
    ])
    timestamp = serializers.DateTimeField(default=datetime.now)
    details = serializers.JSONField(required=False)


class QuizStatisticsSerializer(serializers.Serializer):
    quiz_id = serializers.UUIDField()
    total_attempts = serializers.IntegerField()
    average_score = serializers.FloatField()
    pass_rate = serializers.FloatField()
    average_time_spent = serializers.IntegerField()
    question_statistics = serializers.ListField(child=serializers.DictField())