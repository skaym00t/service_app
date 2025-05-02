from celery import shared_task



@shared_task # Декоратор для создания задачи Celery (можно использовать любое имя)
def set_price(subscription_id): # Функция задачи(можно использовать любое имя)
    from services.models import Subscription
    subscription = Subscription.objects.get(id=subscription_id) # Получаем подписку по id
    new_price = (subscription.service.full_price -
                 subscription.service.full_price * subscription.plan.discount_percent / 100) # Получаем новую цену подписки,
    # c вычетом скидки
    subscription.price = new_price # Присваиваем новую цену подписки
    subscription.save(save_model=False) # Сохраняем подписку(не вызывая метод save у модели Subscription)
