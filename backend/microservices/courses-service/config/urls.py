from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from django.http import JsonResponse

router = routers.DefaultRouter()

def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'courses-service',
        'version': '1.0.0'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/health/', health_check),
    
    # Modules principaux
    path('api/', include('apps.courses.lessons.urls')),
    path('api/', include('apps.courses.certificates.urls')),
]