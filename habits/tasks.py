from datetime import timedelta

import requests
from celery import shared_task
from django.utils import timezone
from rest_framework.generics import get_object_or_404

from config.settings import TELEGRAM_BOT_TOKEN
from habits.models import Habit


@shared_task
def send_tg_notification(habit_id):
    """
    Задача на отправку одного уведомления.
    """
    habit = get_object_or_404(Habit, pk=habit_id)
    message = ""
    if habit.linked_habit:
        message = (
            f"Напоминание!\n"
            f"Действие: {habit.action}\n"
            f"Место: {habit.place}\n"
            f"Связанная привычка: {habit.linked_habit}\n"
            f"Время выполнения: {habit.continuation_time} секунд"
        )
    elif habit.reward:
        message = (
            f"Напоминание!\n"
            f"Действие: {habit.action}\n"
            f"Место: {habit.place}\n"
            f"Награда: {habit.reward}\n"
            f"Время выполнения: {habit.continuation_time} секунд"
        )
    else:
        message = (
            f"Напоминание!\n"
            f"Действие: {habit.action}\n"
            f"Место: {habit.place}\n"
            f"Время выполнения: {habit.continuation_time} секунд"
        )

    url = (
        f"https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/"
        f"sendMessage?chat_id={habit.owner.tg_chat_id}&text={message}"
    )
    requests.get(url=url)
    habit.next_reminder = habit.next_reminder + timezone.timedelta(days=habit.frequency)
    habit.save(update_fields=["next_reminder"])


@shared_task
def check_and_send_tg_notifications():
    """
    Задача на проверку привычек, у которых подошло время уведомления.
    """
    check_time = timezone.now() + timedelta(minutes=1)
    habits_to_notify = Habit.objects.filter(
        next_reminder__lte=check_time, owner__tg_chat_id__isnull=False
    )
    print(habits_to_notify)

    for habit in habits_to_notify:
        send_tg_notification(habit.pk)
