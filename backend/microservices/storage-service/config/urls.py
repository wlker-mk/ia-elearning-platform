from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'storage-service'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/storage/', include('apps.storage.urls')),
    path('api/health/', health_check),
]