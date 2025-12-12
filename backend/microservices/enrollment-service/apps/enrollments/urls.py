from django.urls import path, include

app_name = 'enrollments'

urlpatterns = [
    # Enrollments endpoints
    path('', include('apps.enrollments.enrollments.urls')),
    
    # Progress endpoints
    path('progress/', include('apps.enrollments.progress.urls')),
    
    # Notes endpoints
    path('notes/', include('apps.enrollments.notes.urls')),
]