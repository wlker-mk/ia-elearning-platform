from django.db import models
import uuid

class QuizType(models.TextChoices):
    MULTIPLE_CHOICE = 'MULTIPLE_CHOICE', 'Multiple Choice'
    TRUE_FALSE = 'TRUE_FALSE', 'True/False'
    SHORT_ANSWER = 'SHORT_ANSWER', 'Short Answer'
    ESSAY = 'ESSAY', 'Essay'
    CODING = 'CODING', 'Coding'
    MATCHING = 'MATCHING', 'Matching'
    FILL_BLANK = 'FILL_BLANK', 'Fill in the Blank'


class BaseModel(models.Model):
    """Abstract base model with common fields"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Quiz(BaseModel):
    """Quiz model - managed by Prisma but defined here for Django admin"""
    lesson_id = models.UUIDField()
    course_id = models.UUIDField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    duration = models.IntegerField(null=True, blank=True, help_text="Duration in minutes")
    passing_score = models.FloatField(default=70.0)
    max_attempts = models.IntegerField(default=3)
    randomize_questions = models.BooleanField(default=False)

    class Meta:
        db_table = 'quizzes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['lesson_id', 'course_id']),
        ]

    def __str__(self):
        return self.title


class Question(BaseModel):
    """Question model"""
    quiz_id = models.UUIDField()
    type = models.CharField(max_length=50, choices=QuizType.choices)
    question = models.TextField()
    order = models.IntegerField()
    points = models.FloatField(default=1.0)
    options = models.JSONField(null=True, blank=True)
    correct_answer = models.JSONField(null=True, blank=True)
    explanation = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'questions'
        ordering = ['order']
        indexes = [
            models.Index(fields=['quiz_id', 'order']),
        ]

    def __str__(self):
        return f"Question {self.order} - {self.question[:50]}"


class QuizAttempt(BaseModel):
    """Quiz attempt model"""
    quiz_id = models.UUIDField()
    student_id = models.UUIDField()
    attempt_number = models.IntegerField()
    score = models.FloatField()
    percentage = models.FloatField()
    is_passed = models.BooleanField()
    answers = models.JSONField()
    started_at = models.DateTimeField()
    submitted_at = models.DateTimeField(null=True, blank=True)
    time_spent = models.IntegerField(null=True, blank=True, help_text="Time spent in seconds")

    class Meta:
        db_table = 'quiz_attempts'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['quiz_id', 'student_id']),
        ]

    def __str__(self):
        return f"Attempt {self.attempt_number} - Quiz {self.quiz_id}"


class ProctoringSession(BaseModel):
    """Proctoring session model"""
    quiz_attempt_id = models.UUIDField(unique=True)
    webcam_url = models.URLField(blank=True, null=True)
    screen_url = models.URLField(blank=True, null=True)
    audio_url = models.URLField(blank=True, null=True)
    face_detections = models.JSONField(null=True, blank=True)
    suspicious_activity = models.JSONField(null=True, blank=True)
    tab_switches = models.IntegerField(default=0)
    multiple_faces = models.BooleanField(default=False)
    no_face_detected = models.BooleanField(default=False)
    copy_paste_detected = models.BooleanField(default=False)
    flagged_for_review = models.BooleanField(default=False)
    reviewed_by = models.UUIDField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'proctoring_sessions'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['flagged_for_review']),
        ]

    def __str__(self):
        return f"Proctoring Session - {self.quiz_attempt_id}"