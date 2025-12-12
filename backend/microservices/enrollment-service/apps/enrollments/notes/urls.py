from django.urls import path
from .views import (
    NoteListCreateView,
    NoteDetailView,
    LessonNotesView,
    BookmarkListCreateView,
    BookmarkDetailView,
    CertificateListView,
    CertificateDetailView,
    VerifyCertificateView
)

urlpatterns = [
    # Notes
    path('', NoteListCreateView.as_view(), name='note-list-create'),
    path('<str:note_id>/', NoteDetailView.as_view(), name='note-detail'),
    path('lesson/<str:lesson_id>/', LessonNotesView.as_view(), name='lesson-notes'),
    
    # Bookmarks
    path('bookmarks/', BookmarkListCreateView.as_view(), name='bookmark-list-create'),
    path('bookmarks/<str:bookmark_id>/', BookmarkDetailView.as_view(), name='bookmark-detail'),
    
    # Certificates
    path('certificates/', CertificateListView.as_view(), name='certificate-list'),
    path('certificates/<str:certificate_id>/', CertificateDetailView.as_view(), name='certificate-detail'),
    path('certificates/verify/<str:verification_code>/', VerifyCertificateView.as_view(), name='verify-certificate'),
] 