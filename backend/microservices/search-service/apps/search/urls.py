from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SearchIndexViewSet, SearchViewSet, HealthCheckViewSet

router = DefaultRouter()

# Register viewsets
router.register(r'indexes', SearchIndexViewSet, basename='search-index')
router.register(r'search', SearchViewSet, basename='search')
router.register(r'health', HealthCheckViewSet, basename='health')

urlpatterns = [
    path('', include(router.urls)),
]