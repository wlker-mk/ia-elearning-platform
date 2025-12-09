from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LessonsViewSet, ResourcesViewSet

router = DefaultRouter()
router.register(r'lessons', LessonsViewSet, basename='lesson')
router.register(r'resources', ResourcesViewSet, basename='resource')

urlpatterns = [
    path('', include(router.urls)),
]