from django.apps import AppConfig
import logging

            import apps.courses.courses.signals
            import apps.courses.lessons.signals
            import apps.courses.certificates.signals
        import threading
        from apps.courses.courses.signals import start_event_consumers

logger = logging.getLogger(__name__)


class CoursesConfig(AppConfig):
    """
    Configuration principale du package courses.

    Ce package regroupe tous les modules liés aux cours :
    - courses : Gestion des cours et structure
    - lessons : Gestion des leçons
    - certificates : Gestion des certificats
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.courses'
    verbose_name = 'Courses Management System'

    def ready(self):
        """
        Initialisation du package quand Django démarre.
        Charge tous les signals et configurations nécessaires.
        """
        logger.info("Initializing Courses package...")

        # Importer les signals de tous les sous-modules
        try:
            logger.info("✓ Courses signals loaded")
        except ImportError as e:
            logger.warning(f"Could not load courses signals: {e}")

        try:
            logger.info("✓ Lessons signals loaded")
        except ImportError as e:
            logger.warning(f"Could not load lessons signals: {e}")

        try:
            logger.info("✓ Certificates signals loaded")
        except ImportError as e:
            logger.warning(f"Could not load certificates signals: {e}")

        # Démarrer les consumers RabbitMQ en arrière-plan
        # Note: En production, ceci devrait être un processus séparé
        # self._start_event_consumers()

        logger.info("✓ Courses package initialized successfully")

    def _start_event_consumers(self):
        """
        Démarrer les consumers d'événements RabbitMQ.
        À utiliser uniquement en développement.
        En production, lancer comme processus séparé.
        """
        consumer_thread = threading.Thread(
            target=start_event_consumers,
            daemon=True
        )
        consumer_thread.start()
        logger.info("✓ RabbitMQ event consumers started")
