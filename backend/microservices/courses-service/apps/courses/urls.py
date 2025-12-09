"""
URLs principales du package courses.
Regroupe toutes les routes des sous-modules.
"""

from django.urls import path, include

app_name = 'courses'

urlpatterns = [
    # Module courses (cours, sections, catégories, tags, wishlist)
    path('', include('apps.courses.courses.urls')),
    
    # Module lessons (leçons, ressources)
    path('', include('apps.courses.lessons.urls')),
    
    # Module certificates (certificats, templates)
    path('', include('apps.courses.certificates.urls')),
]