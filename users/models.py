from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Кастомная модель юзера.
    """

    username = None

    email = models.EmailField(
        unique=True,
        verbose_name="почта",
        help_text="Укажите почту",
        max_length=50
    )
    tg_chat_id = models.CharField(
        verbose_name="Чат айди телеграмма",
        blank=True,
        null=True,
        help_text="Введите ваш телеграм chat_id",
        max_length=255,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["tg_chat_id"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
