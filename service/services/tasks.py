import datetime

from celery import shared_task
from celery_singleton import Singleton
from django.db import transaction
from django.db.models import F


@shared_task(base=Singleton) # Декоратор для создания задачи Celery (можно использовать любое имя)
def set_price(subscription_id): # Функция задачи(можно использовать любое имя)
    from services.models import Subscription
    # Первый способ - получаем подписку по id и сохраняем ее (не рекомендуется, так как это
    # может вызвать проблемы с производительностью, так как вызываем N+1 запросов к базе данных)
    # new_price = (subscription.service.full_price -
    #              subscription.service.full_price * subscription.plan.discount_percent / 100) # Получаем новую цену подписки,
    # # c вычетом скидки
    # subscription.price = new_price # Присваиваем новую цену подписки
    with transaction.atomic(): # Используем транзакцию, чтобы избежать проблем с целостностью данных
        subscription = Subscription.objects.select_for_update().filter(id=subscription_id).annotate(
            annotated_price=F('service__full_price') -
                            F('service__full_price') * (F('plan__discount_percent') / 100.00)).first()
        # Получаем подписку по id и аннотируем ее, чтобы получить цену подписки с учетом скидки
        subscription.price = subscription.annotated_price # Присваиваем новую цену подписки
        subscription.save(save_model=False) # Сохраняем подписку(не вызывая метод save у модели Subscription)

@shared_task(base=Singleton) # Декоратор для создания задачи Celery (можно использовать любое имя)
def set_comment(subscription_id):
    from services.models import Subscription # Импортируем модель Subscription
    with transaction.atomic(): # Используем транзакцию, чтобы избежать проблем с целостностью данных
        subscription = Subscription.objects.select_for_update().get(id=subscription_id) # Получаем подписку по id
        subscription.comment = str(datetime.datetime.now()) # Присваиваем комментарий подписки текущее время
        subscription.save() # Сохраняем подписку