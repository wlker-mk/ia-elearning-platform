from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CertificatesViewSet, CertificateTemplatesViewSet

router = DefaultRouter()
router.register(r'certificates', CertificatesViewSet, basename='certificate')
router.register(r'templates', CertificateTemplatesViewSet, basename='certificate-template')

urlpatterns = [
    path('', include(router.urls)),
]