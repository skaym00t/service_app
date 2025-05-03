from django.core.validators import MaxValueValidator
from django.db import models

from clients.models import Client
from services.tasks import set_price, set_comment


class Service(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название услуги')  # Название услуги
    full_price = models.PositiveIntegerField(default=0, verbose_name='Стоимость услуги')  # Полная цена

    class Meta:  # Опции модели
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    def __str__(self):  # Строковое представление
        return f'{self.name} - {self.full_price} руб.'

    def __init__(self, *args, **kwargs):  # Конструктор класса
        super().__init__(*args, **kwargs)   # Вызываем конструктор родительского класса
        self.__full_price = self.full_price  # Сохраняем процент скидки в переменной

    def save(self, *args, **kwargs): # Переопределяем метод сохранения модели
        if self.__full_price != self.full_price:  # Если процент скидки изменился
            for subscription in self.subscriptions.all():  # Для всех подписок, связанных с планом
                set_price.delay(subscription.id) # Вызываем задачу Celery для расчета цены подписки
                set_comment.delay(subscription.id)  # Вызываем задачу Celery для изменения комментария подписки
        return super().save(*args, **kwargs)

class Plan(models.Model):
    PLAN_TYPES = (
        ('full', 'Полный'),
        ('student', 'Студенческий'),
        ('discount', 'Скидка'),
    ) # Типы планов

    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, verbose_name='Тип плана')  # Тип плана (choices для выбора из списка)
    discount_percent = models.PositiveIntegerField(default=0,
                                                   validators=[MaxValueValidator(100)],
                                                   verbose_name='Процент скидки')  # Процент скидки (по умолчанию 0, максимум 100)

    class Meta:  # Опции модели
        verbose_name = 'План'
        verbose_name_plural = 'Планы'

    def __str__(self):  # Строковое представление
        return f'{self.plan_type} - {self.discount_percent}%'

    def __init__(self, *args, **kwargs):  # Конструктор класса
        super().__init__(*args, **kwargs)   # Вызываем конструктор родительского класса
        self.__discount_percent = self.discount_percent  # Сохраняем процент скидки в переменной

    def save(self, *args, **kwargs): # Переопределяем метод сохранения модели
        if self.__discount_percent != self.discount_percent:  # Если процент скидки изменился
            for subscription in self.subscriptions.all():  # Для всех подписок, связанных с планом
                set_price.delay(subscription.id) # Вызываем задачу Celery для расчета цены подписки
                set_comment.delay(subscription.id) # Вызываем задачу Celery для изменения комментария подписки
        return super().save(*args, **kwargs)


class Subscription(models.Model):
    client = models.ForeignKey(Client, related_name='subscriptions', on_delete=models.PROTECT, verbose_name='Клиент')  # Связь с клиентом
    service = models.ForeignKey(Service, related_name='subscriptions', on_delete=models.PROTECT, verbose_name='Услуга')  # Связь с услугой
    plan = models.ForeignKey(Plan, related_name='subscriptions', on_delete=models.PROTECT, verbose_name='План')  # Связь с планом
    price = models.PositiveIntegerField(default=0, verbose_name='Цена подписки')  # Цена подписки (по умолчанию 0)
    comment = models.CharField(default='', max_length=200, verbose_name='Комментарии') # Комментарии к подписке (по умолчанию пустая строка)

    class Meta:  # Опции модели
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):  # Строковое представление
        return f'{self.client.user.username} - {self.service.name} - {self.plan.plan_type}'

    def save(self, *args, save_model=True, **kwargs):  # Переопределяем метод сохранения модели(save_model - для того,
        # чтобы не сохранять модель при вызове метода save у модели Subscription)
        if save_model: # Если save_model = True, то сохраняем модель
            set_price.delay(self.id) # Вызываем задачу Celery для расчета цены подписки(отправляем задачу в очередь)
            set_comment.delay(self.id)  # Вызываем задачу Celery для изменения комментария подписки
        return super().save(*args, **kwargs)  # Вызываем метод save у родительского класса(models.Model)
