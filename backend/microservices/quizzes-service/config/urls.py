from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    """Health check endpoint"""
    return JsonResponse({'status': 'healthy', 'service': 'quizzes-service'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/quizzes/', include('apps.quizzes.urls')),
    path('api/health/', health_check),
]
