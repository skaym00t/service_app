from django.core.validators import MaxValueValidator
from django.db import models

from clients.models import Client


class Service(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название услуги')  # Название услуги
    full_price = models.PositiveIntegerField(default=0, verbose_name='Стоимость услуги')  # Полная цена

    class Meta:  # Опции модели
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    def __str__(self):  # Строковое представление
        return f'{self.name} - {self.full_price} руб.'

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

class Subscription(models.Model):
    client = models.ForeignKey(Client, related_name='subscriptions', on_delete=models.PROTECT, verbose_name='Клиент')  # Связь с клиентом
    service = models.ForeignKey(Service, related_name='subscriptions', on_delete=models.PROTECT, verbose_name='Услуга')  # Связь с услугой
    plan = models.ForeignKey(Plan, related_name='subscriptions', on_delete=models.PROTECT, verbose_name='План')  # Связь с планом

    class Meta:  # Опции модели
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):  # Строковое представление
        return f'{self.client.user.username} - {self.service.name} - {self.plan.plan_type}'
