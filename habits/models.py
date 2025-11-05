import datetime

from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError


class Habit(models.Model):
    """
    Модель привычки.
    """

    owner = models.ForeignKey(
        "users.User",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name="создатель привычки",
    )
    place = models.CharField(
        verbose_name="место действия",
        null=True,
        blank=True,
        max_length=255,
    )
    time = models.TimeField(
        verbose_name="время действия", default=datetime.time(hour=18)
    )
    action = models.CharField(verbose_name="действие", null=True, blank=True)
    is_pleasant = models.BooleanField(verbose_name="признак приятной привычки")
    linked_habit = models.ForeignKey(
        "self",
        verbose_name="связанная привычка",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"is_pleasant": True},
    )
    is_good = models.BooleanField(verbose_name="признак полезной привычки")
    frequency = models.PositiveIntegerField(verbose_name="периодичность в днях")
    reward = models.CharField(
        verbose_name="вознаграждение",
        max_length=255,
        blank=True,
        null=True,
    )
    continuation_time = models.SmallIntegerField(
        verbose_name="время выполнения в секундах"
    )
    is_public = models.BooleanField(verbose_name="признак публичности")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    next_reminder = models.DateTimeField(
        verbose_name="дата и время следующего уведомления",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "привычка"
        verbose_name_plural = "привычки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.owner.email}: {self.action} в {self.time}"

    def clean(self):
        """
        Валидация на уровне модели.
        """
        if self.is_pleasant:
            if self.reward:
                raise ValidationError(
                    "Приятная привычка не может иметь вознаграждение."
                )
            if self.linked_habit:
                raise ValidationError(
                    "Приятная привычка не может \
                    быть связана с другой привычкой"
                )

        if self.linked_habit and self.reward:
            raise ValidationError(
                "Привычка не может иметь связанную привычку и вознаграждение."
            )

        if self.linked_habit and not self.linked_habit.is_pleasant:
            raise ValidationError("Связанная привычка должна быть приятной")

        if not self.is_good and not self.is_pleasant:
            raise ValidationError("Привычка должна быть либо полезной, либо приятной")

    def calculate_next_reminder(self):
        """
        Расчет следующего напоминания от текущего момента времени.
        """
        now = timezone.now()

        today_with_habit_time = timezone.make_aware(
            timezone.datetime.combine(now.date(), self.time)
        )

        if today_with_habit_time <= now:
            next_date = now.date() + timezone.timedelta(days=self.frequency)
        else:
            next_date = now.date()

        next_reminder_datetime = timezone.make_aware(
            timezone.datetime.combine(next_date, self.time)
        )

        return next_reminder_datetime

    def save(self, *args, **kwargs):
        """
        Расчет next_reminder привычки при сохранении.
        """
        self.next_reminder = self.calculate_next_reminder()
        super().save(*args, **kwargs)
