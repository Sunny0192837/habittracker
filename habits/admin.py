from django.contrib import admin

from habits.models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    """
    Регистрация модели привычки в админке
    """

    list_display = ("id", "action", "is_public")
    search_fields = (
        "action",
        "place",
        "reward",
    )
