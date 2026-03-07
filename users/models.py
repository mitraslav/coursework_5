from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    telegram_chat_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='ID чата в Telegram'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']