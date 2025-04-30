from django.contrib.auth.models import User
from django.db import models

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT) # Связь с пользователем
    company_name = models.CharField(max_length=100) # Название компании
    full_address = models.CharField(max_length=100) # Полный адрес

    class Meta: # Опции модели
        verbose_name = 'Клиенты' # Имя в админке
        verbose_name_plural = 'Клиенты' # Множественное имя в админке
    def __str__(self): # Строковое представление
        return f'{self.user.username} - {self.company_name}'
