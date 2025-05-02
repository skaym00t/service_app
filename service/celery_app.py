import os
import time

from celery import Celery
from django.conf import settings

# ``` Настройка Celery для Django проекта ```

os.environ.setdefault('DJANGO_SETTINGS_MODULE','service.settings') # Указываем настройки Django

app = Celery('service') # Создаем экземпляр Celery
app.config_from_object('django.conf:settings') # Загружаем настройки Django
app.conf.broker_url = settings.CELERY_BROKER_URL # Указываем брокер сообщений
# CELERY_BROKER_URL нужно прописать в .env файл или в settings.py
app.autodiscover_tasks() # Автоматически находим задачи в приложениях Django

# ``` Таски Celery ```

@app.task() # Декоратор для создания задачи Celery
def debug_task(): # Функция задачи(можно использовать любое имя) это пример задачи, которая будет выполняться
    time.sleep(20) # Задержка на 20 секунд
    print('Hello form debug_task') # Выводим информацию о запросе
