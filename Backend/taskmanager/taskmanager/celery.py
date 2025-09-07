import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmanager.settings')

# Создаем экземпляр Celery
app = Celery('taskmanager')

# Загружаем настройки из Django
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

