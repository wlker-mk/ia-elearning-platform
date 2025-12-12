from django.urls import path
from .views import (
    EnrollmentListCreateView,
    EnrollmentDetailView,
    CompleteEnrollmentView,
    MyEnrollmentsView,
    EnrollmentStatsView
)

urlpatterns = [
    path('', EnrollmentListCreateView.as_view(), name='enrollment-list-create'),
    path('my-enrollments/', MyEnrollmentsView.as_view(), name='my-enrollments'),
    path('stats/', EnrollmentStatsView.as_view(), name='enrollment-stats'),
    path('<str:enrollment_id>/', EnrollmentDetailView.as_view(), name='enrollment-detail'),
    path('<str:enrollment_id>/complete/', CompleteEnrollmentView.as_view(), name='enrollment-complete'),
]