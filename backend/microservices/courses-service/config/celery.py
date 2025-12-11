import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings
    import logging
        from apps.courses.courses.signals import publish_event
from celery.signals import task_failure, task_success

    import logging
"""
Celery Configuration for courses-service
"""
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('courses_service')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Celery Configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Periodic Tasks Schedule
app.conf.beat_schedule = {
    # Nettoyer les cours non publiés (tous les jours à 2h du matin)
    'cleanup-unpublished-courses': {
        'task': 'apps.courses.courses.tasks.cleanup_unpublished_courses',
        'schedule': crontab(hour=2, minute=0),
    },

    # Calculer les cours tendances (toutes les heures)
    'calculate-trending-courses': {
        'task': 'apps.courses.courses.tasks.calculate_trending_courses',
        'schedule': crontab(minute=0),  # Chaque heure
    },

    # Vérifier les certificats expirés (tous les jours à 3h)
    'check-expired-certificates': {
        'task': 'apps.courses.certificates.tasks.check_expired_certificates',
        'schedule': crontab(hour=3, minute=0),
    },

    # Générer les analytics des certificats (tous les jours à 4h)
    'generate-certificate-analytics': {
        'task': 'apps.courses.certificates.tasks.generate_certificate_analytics',
        'schedule': crontab(hour=4, minute=0),
    },

    # Nettoyer les anciennes vérifications (toutes les semaines)
    'cleanup-old-verifications': {
        'task': 'apps.courses.certificates.tasks.cleanup_old_certificate_verifications',
        'schedule': crontab(day_of_week=0, hour=5, minute=0),  # Dimanche à 5h
    },

    # Vérifier les ressources cassées (toutes les semaines)
    'check-broken-resources': {
        'task': 'apps.courses.lessons.tasks.check_broken_resources',
        'schedule': crontab(day_of_week=1, hour=6, minute=0),  # Lundi à 6h
    },

    # Valider les templates de certificats (tous les mois)
    'validate-certificate-templates': {
        'task': 'apps.courses.certificates.tasks.validate_certificate_templates',
        'schedule': crontab(day_of_month=1, hour=7, minute=0),  # 1er du mois à 7h
    },
}

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Task de debug pour tester Celery"""
    print(f'Request: {self.request!r}')


@app.task(name='health_check')
def health_check():
    """Health check task pour monitoring"""
    return {'status': 'healthy', 'service': 'courses-service'}


# Task Error Handler
@app.task(bind=True, max_retries=3)
def handle_task_error(self, task_id, exception):
    """Gérer les erreurs de tâches"""
    logger = logging.getLogger(__name__)

    logger.error(f"Task {task_id} failed with error: {exception}")

    # Publier un événement pour monitoring
    try:
        publish_event('task.failed', {
            'taskId': task_id,
            'error': str(exception),
            'retries': self.request.retries
        })
    except Exception as e:
        logger.error(f"Failed to publish task error event: {e}")


# Celery Signal Handlers
@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, **kwargs):
    """Handler pour les échecs de tâches"""
    handle_task_error.delay(task_id, str(exception))


@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    """Handler pour les succès de tâches"""
    logger = logging.getLogger(__name__)
    logger.info(f"Task {sender.name} completed successfully")
