from django.urls import path
from .views import (
    ProgressCreateUpdateView,
    ProgressDetailView,
    CourseProgressView,
    ProgressStatsView,
    StartStudySessionView,
    EndStudySessionView,
    ActiveStudySessionView
)

urlpatterns = [
    path('', ProgressCreateUpdateView.as_view(), name='progress-create-update'),
    path('stats/', ProgressStatsView.as_view(), name='progress-stats'),
    path('course/<str:course_id>/', CourseProgressView.as_view(), name='course-progress'),
    path('<str:progress_id>/', ProgressDetailView.as_view(), name='progress-detail'),
    
    # Study sessions
    path('sessions/start/', StartStudySessionView.as_view(), name='start-session'),
    path('sessions/<str:session_id>/end/', EndStudySessionView.as_view(), name='end-session'),
    path('sessions/active/', ActiveStudySessionView.as_view(), name='active-session'),
]