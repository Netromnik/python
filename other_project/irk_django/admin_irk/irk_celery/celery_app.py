import os
from celery import Celery
from .config import BEAT_SCHEDULE

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

app = Celery('irk')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.timezone = 'Asia/Irkutsk'
app.conf.beat_schedule = BEAT_SCHEDULE
