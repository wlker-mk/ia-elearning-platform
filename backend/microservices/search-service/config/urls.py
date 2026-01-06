from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from django.http import JsonResponse

router = routers.DefaultRouter()

def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'search-service'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.search.urls')),
    path('api/health/', health_check, name='health'),
]