"""
Courses Package
===============

Package principal regroupant tous les modules liés aux cours :
- courses : Gestion des cours, sections, catégories, tags
- lessons : Gestion des leçons et ressources pédagogiques
- certificates : Génération et gestion des certificats

Ce package fait partie du courses-service qui gère tout le contenu
pédagogique de la plateforme e-learning.
"""

default_app_config = 'apps.courses.apps.CoursesConfig'

__version__ = '1.0.0'
__author__ = 'Your Team'

# Modules disponibles
__all__ = [
    'courses',
    'lessons',
    'certificates',
]