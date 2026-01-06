import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('search_service')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# Periodic tasks
app.conf.beat_schedule = {
    'cleanup-old-tracking-daily': {
        'task': 'apps.search.tasks.cleanup_old_tracking_task',
        'schedule': crontab(hour=2, minute=0),  # Run at 2 AM daily
        'args': (30,)  # Keep last 30 days
    },
    'generate-search-report-weekly': {
        'task': 'apps.search.tasks.generate_search_report_task',
        'schedule': crontab(day_of_week=1, hour=8, minute=0),  # Monday 8 AM
        'args': (7,)
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')