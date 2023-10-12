from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knowverwatch.settings')

app = Celery('knowverwatch')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.broker_url = 'redis://localhost:6379/0'

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Celery Beat settings
app.conf.beat_schedule = {

    'update-database': {
        'task': 'stats.tasks.update_the_whole_database',
        'schedule': crontab(hour=4, minute=0),
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request {self.request!r}')
