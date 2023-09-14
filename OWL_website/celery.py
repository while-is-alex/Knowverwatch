from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OWL_website.settings')

app = Celery('OWL_website')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.broker_url = 'redis://localhost:6379/0'

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Celery Beat settings
app.conf.beat_schedule = {
    'update-teams': {
        'task': 'stats.tasks.update_all_teams_database',
        'schedule': crontab(hour=2, minute=0),
    },
    'update-players': {
        'task': 'stats.tasks.update_all_players_database',
        'schedule': crontab(hour=3, minute=0),
    },
    'update-segments': {
        'task': 'stats.tasks.update_all_segments_database',
        'schedule': crontab(hour=4, minute=0),
    },
    'update-matches': {
        'task': 'stats.tasks.update_all_matches_database',
        'schedule': crontab(hour=5, minute=0),
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request {self.request!r}')
