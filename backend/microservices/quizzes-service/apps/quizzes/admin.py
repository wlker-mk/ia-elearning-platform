from django.contrib import admin
from .models import Quiz, Question, QuizAttempt, ProctoringSession


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'course_id', 'lesson_id', 'duration', 'passing_score', 'max_attempts', 'created_at']
    list_filter = ['passing_score', 'randomize_questions', 'created_at']
    search_fields = ['title', 'description', 'course_id', 'lesson_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'course_id', 'lesson_id')
        }),
        ('Quiz Settings', {
            'fields': ('duration', 'passing_score', 'max_attempts', 'randomize_questions')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_preview', 'quiz_id', 'type', 'order', 'points', 'created_at']
    list_filter = ['type', 'points', 'created_at']
    search_fields = ['question', 'quiz_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['quiz_id', 'order']
    
    fieldsets = (
        ('Question Details', {
            'fields': ('quiz_id', 'type', 'question', 'order', 'points')
        }),
        ('Answer Configuration', {
            'fields': ('options', 'correct_answer', 'explanation')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def question_preview(self, obj):
        return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
    question_preview.short_description = 'Question'


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['quiz_id', 'student_id', 'attempt_number', 'score', 'percentage', 'is_passed', 'submitted_at']
    list_filter = ['is_passed', 'created_at', 'submitted_at']
    search_fields = ['quiz_id', 'student_id']
    readonly_fields = ['id', 'created_at', 'updated_at', 'score', 'percentage', 'is_passed', 'time_spent']
    ordering = ['-started_at']
    
    fieldsets = (
        ('Attempt Information', {
            'fields': ('quiz_id', 'student_id', 'attempt_number')
        }),
        ('Results', {
            'fields': ('score', 'percentage', 'is_passed', 'time_spent')
        }),
        ('Answers', {
            'fields': ('answers',),
            'classes': ('collapse',)
        }),
        ('Timing', {
            'fields': ('started_at', 'submitted_at')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProctoringSession)
class ProctoringSessionAdmin(admin.ModelAdmin):
    list_display = [
        'quiz_attempt_id', 'tab_switches', 'multiple_faces', 
        'no_face_detected', 'copy_paste_detected', 'flagged_for_review',
        'reviewed_by', 'started_at'
    ]
    list_filter = [
        'flagged_for_review', 'multiple_faces', 'no_face_detected',
        'copy_paste_detected', 'started_at'
    ]
    search_fields = ['quiz_attempt_id', 'reviewed_by']
    readonly_fields = ['id', 'created_at', 'updated_at', 'started_at']
    ordering = ['-started_at']
    
    fieldsets = (
        ('Session Information', {
            'fields': ('quiz_attempt_id', 'started_at', 'ended_at')
        }),
        ('Media URLs', {
            'fields': ('webcam_url', 'screen_url', 'audio_url'),
            'classes': ('collapse',)
        }),
        ('Detection Flags', {
            'fields': (
                'tab_switches', 'multiple_faces', 'no_face_detected',
                'copy_paste_detected', 'flagged_for_review'
            )
        }),
        ('Detection Data', {
            'fields': ('face_detections', 'suspicious_activity'),
            'classes': ('collapse',)
        }),
        ('Review Information', {
            'fields': ('reviewed_by', 'reviewed_at', 'review_notes')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['flag_for_review', 'unflag_for_review']
    
    def flag_for_review(self, request, queryset):
        updated = queryset.update(flagged_for_review=True)
        self.message_user(request, f'{updated} sessions flagged for review.')
    flag_for_review.short_description = 'Flag selected sessions for review'
    
    def unflag_for_review(self, request, queryset):
        updated = queryset.update(flagged_for_review=False)
        self.message_user(request, f'{updated} sessions unflagged.')
    unflag_for_review.short_description = 'Remove review flag from selected sessions'