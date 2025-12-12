from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    QuizViewSet,
    QuestionViewSet,
    QuizAttemptViewSet,
    ProctoringViewSet
)

router = DefaultRouter()
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'attempts', QuizAttemptViewSet, basename='quiz-attempt')
router.register(r'proctoring', ProctoringViewSet, basename='proctoring')

urlpatterns = [
    path('', include(router.urls)),
]