import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('enrollments_service')

# Load config from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'update-enrollment-statuses': {
        'task': 'apps.enrollments.enrollments.tasks.update_enrollment_statuses',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
    'cleanup-inactive-sessions': {
        'task': 'apps.enrollments.progress.tasks.cleanup_inactive_sessions',
        'schedule': crontab(minute=0, hour=2),  # Daily at 2 AM
    },
    'generate-progress-reports': {
        'task': 'apps.enrollments.progress.tasks.generate_daily_progress_reports',
        'schedule': crontab(minute=0, hour=8),  # Daily at 8 AM
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')