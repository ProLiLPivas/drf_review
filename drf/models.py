from django.contrib.auth.models import AbstractUser
from django.db import models

from . import managers


class User(AbstractUser):
    inn = models.PositiveIntegerField(verbose_name='ИНН', unique=True)
    money_amount = models.DecimalField(verbose_name='Счёт', decimal_places=2, max_digits=100)

    manager = managers.UsersManager()

    def __str__(self):
        return f'<User {self.username} inn={self.inn}>'
