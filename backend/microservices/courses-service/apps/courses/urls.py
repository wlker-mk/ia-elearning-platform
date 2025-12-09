from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CoursesViewSet,
    SectionsViewSet,
    LessonsViewSet,
    ResourcesViewSet,
    CategoriesViewSet,
    TagsViewSet,
    WishlistViewSet
)

router = DefaultRouter()
router.register(r'sections', SectionsViewSet, basename='section')
router.register(r'lessons', LessonsViewSet, basename='lesson')
router.register(r'resources', ResourcesViewSet, basename='resource')
router.register(r'categories', CategoriesViewSet, basename='category')
router.register(r'tags', TagsViewSet, basename='tag')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')

urlpatterns = [
    path('', include(router.urls)),
]