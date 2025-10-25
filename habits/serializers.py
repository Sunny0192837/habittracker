from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from habits.models import Habit


class HabitSerializer(ModelSerializer):
    """
    Сериализатор для привычки.
    """

    class Meta:
        model = Habit
        fields = "__all__"

    def validate(self, data):
        """
        Валидация данных привычки
        """
        if self.instance:
            is_pleasant = data.get("is_pleasant", self.instance.is_pleasant)
            is_good = data.get("is_good", self.instance.is_good)
            linked_habit = data.get("linked_habit", self.instance.linked_habit)
            reward = data.get("reward", self.instance.reward)
            frequency = data.get("frequency", self.instance.frequency)
            continuation_time = data.get(
                "continuation_time",
                self.instance.continuation_time
            )
        else:
            is_pleasant = data.get("is_pleasant")
            is_good = data.get("is_good")
            linked_habit = data.get("linked_habit")
            reward = data.get("reward")
            frequency = data.get("frequency")
            continuation_time = data.get("continuation_time")

        if continuation_time and continuation_time > 120:
            raise serializers.ValidationError(
                "Время выполнения не может превышать 120 секунд"
            )

        if frequency is not None:
            if frequency < 1:
                raise serializers.ValidationError(
                    "Частота не может быть меньше 1 дня"
                )
            if frequency > 7:
                raise serializers.ValidationError(
                    "Нельзя выполнять привычку реже, чем 1 раз в 7 дней"
                )

        if is_pleasant:
            if reward:
                raise serializers.ValidationError(
                    "Приятная привычка не может иметь вознаграждение."
                )
            if linked_habit:
                raise serializers.ValidationError(
                    "Приятная привычка не может быть связана с другой привычкой"
                )

        if linked_habit and reward:
            raise serializers.ValidationError(
                "Привычка не может иметь связанную привычку и вознаграждение."
            )

        if linked_habit and not linked_habit.is_pleasant:
            raise serializers.ValidationError("Связанная привычка должна быть приятной")

        if not is_good and not is_pleasant:
            raise serializers.ValidationError(
                "Привычка должна быть либо полезной, либо приятной"
            )

        return data
