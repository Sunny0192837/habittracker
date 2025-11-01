import datetime

from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase

from habits.models import Habit
from users.models import User


@freeze_time("2025-10-24 12:00:00+07:00")
class HabitTestCase(APITestCase):

    def setUp(self):
        """Наполнение базы данных."""
        super().setUp()
        self.user = User.objects.create(email="aboba@example.com")
        self.superuser = User.objects.create(
            email="superuser@example.com", is_superuser=True
        )
        self.client.force_authenticate(user=self.user)
        self.habit = Habit.objects.create(
            owner=self.user,
            place="Дома",
            time=datetime.time(hour=12),
            action="Выпить стакан воды",
            is_pleasant=False,
            is_good=True,
            frequency=1,
            reward="Cъесть конфету",
            continuation_time=5,
            is_public=False,
        )
        self.public_habit = Habit.objects.create(
            owner=self.superuser,
            place="В баре",
            time=datetime.time(hour=18),
            action="Выпить стакан водки",
            is_pleasant=False,
            is_good=True,
            frequency=1,
            reward="Cъесть конфету",
            continuation_time=5,
            is_public=True,
        )
        self.private_habit = Habit.objects.create(
            owner=self.user,
            place="На улице",
            time=datetime.time(hour=12),
            action="Пробежать километр",
            is_pleasant=False,
            is_good=True,
            frequency=3,
            reward="Cъесть конфету",
            continuation_time=5,
            is_public=False,
        )

    def test_habit_create(self):
        """Тестирование создания привычки."""
        url = reverse_lazy("habits:habit_create")
        data = {
            "place": "Дома",
            "time": "17:35:00",
            "action": "Выпить стакан воды",
            "is_pleasant": False,
            "is_good": True,
            "frequency": 1,
            "reward": "Позалипать в тик-ток",
            "continuation_time": 15,
            "is_public": True,
        }
        response = self.client.post(url, data)
        result = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.all().count(), 4)

        self.assertEqual(result["place"], "Дома")
        self.assertEqual(result["time"], "17:35:00")
        self.assertEqual(result["action"], "Выпить стакан воды")
        self.assertEqual(result["is_pleasant"], False)
        self.assertEqual(result["is_good"], True)
        self.assertEqual(result["frequency"], 1)
        self.assertEqual(result["reward"], "Позалипать в тик-ток")
        self.assertEqual(result["continuation_time"], 15)
        self.assertEqual(result["is_public"], True)
        self.assertEqual(result["created_at"], "2025-10-24T12:00:00+07:00")
        self.assertEqual(result["updated_at"], "2025-10-24T12:00:00+07:00")
        self.assertEqual(result["next_reminder"], "2025-10-24T17:35:00+07:00")
        self.assertEqual(result["owner"], self.user.pk)
        self.assertEqual(result["linked_habit"], None)

    def test_habit_delete(self):
        """Тест удаления привычки."""
        initial_count = Habit.objects.count()
        url = reverse_lazy("habits:habit_delete", args=(self.habit.pk,))
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), initial_count - 1)
        self.assertFalse(Habit.objects.filter(pk=self.habit.pk).exists())

    def test_linked_habit_with_reward(self):
        """ Исключить одновременный выбор связанной привычки и указания вознаграждения. """
        pleasant_habit = Habit.objects.create(
            owner=self.user,
            place="Дома",
            time=datetime.time(hour=18),
            action="Медитация",
            is_pleasant=True,
            is_public=True,
            is_good=False,
            frequency=1,
            continuation_time=10
        )

        url = reverse_lazy("habits:habit_create")
        data = {
            "place": "Дома",
            "time": "17:35:00",
            "action": "Выпить стакан воды",
            "is_pleasant": False,
            "is_public": True,
            "is_good": True,
            "frequency": 1,
            "continuation_time": 15,
            "reward": "Позалипать в тик-ток",
            "linked_habit": pleasant_habit.pk,
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Привычка не может иметь связанную привычку и вознаграждение", str(response.json()))

    def test_continuation_time(self):
        """ Время выполнения. """
        url = reverse_lazy("habits:habit_create")
        data = {
            "place": "Дома",
            "time": "17:35:00",
            "action": "Выпить стакан воды",
            "is_pleasant": False,
            "is_public": True,
            "is_good": True,
            "frequency": 1,
            "continuation_time": 121,
            "reward": "Позалипать в тик-ток",
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Время выполнения не может превышать 120 секунд", str(response.json()))

    def test_pleasant_habit_with_reward(self):
        """У приятной привычки не может быть вознаграждения или связанной привычки."""
        url = reverse_lazy("habits:habit_create")

        data_with_reward = {
            "place": "Дома",
            "time": "17:35",
            "action": "Медитация",
            "is_pleasant": True,
            "is_public": True,
            "frequency": 1,
            "continuation_time": 15,
            "reward": "Чай",
        }

        response = self.client.post(url, data_with_reward)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Приятная привычка не может иметь вознаграждение.", str(response.json()))

    def test_frequency_min(self):
        """ Нельзя выполнять привычку реже, чем 1 раз в 7 дней. """
        url = reverse_lazy("habits:habit_create")
        data = {
            "place": "Дома",
            "time": "17:35",
            "action": "Выпить стакан воды",
            "is_public": True,
            "is_good": True,
            "frequency": 8,
            "continuation_time": 15,
            "reward": "Позалипать в тик-ток",
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Нельзя выполнять привычку реже, чем 1 раз в 7 дней", str(response.json()))

    def test_frequency_max(self):
        """ Нельзя не выполнять привычку более 7 дней. """
        url = reverse_lazy("habits:habit_create")
        data = {
            "place": "Дома",
            "time": "17:35",
            "action": "Выпить стакан воды",
            "is_public": True,
            "is_good": True,
            "frequency": 0,
            "continuation_time": 15,
            "reward": "Позалипать в тик-ток",
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Частота не может быть меньше 1 дня", str(response.json()))

    def test_habit_delete_403(self):
        """Тест доступа на удаление."""
        other_user = User.objects.create(email="other@example.com")
        other_habit = Habit.objects.create(
            owner=other_user,
            place="На улице",
            time=datetime.time(hour=12),
            action="Пробежать километр",
            is_pleasant=False,
            is_good=True,
            frequency=3,
            reward="Cъесть конфету",
            continuation_time=5,
            is_public=False,
        )

        url = reverse_lazy("habits:habit_delete", args=(other_habit.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_habit_retrieve(self):
        """Тест получения одной привычки."""
        url = reverse_lazy("habits:habit_retrieve", args=(self.habit.pk,))
        response = self.client.get(url)
        result = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result["id"], self.habit.pk)
        self.assertEqual(result["place"], "Дома")
        self.assertEqual(result["time"], "12:00:00")
        self.assertEqual(result["action"], "Выпить стакан воды")
        self.assertEqual(result["is_pleasant"], False)
        self.assertEqual(result["is_good"], True)
        self.assertEqual(result["frequency"], 1)
        self.assertEqual(result["reward"], "Cъесть конфету")
        self.assertEqual(result["continuation_time"], 5)
        self.assertEqual(result["is_public"], False)
        self.assertEqual(result["created_at"], "2025-10-24T12:00:00+07:00")
        self.assertEqual(result["updated_at"], "2025-10-24T12:00:00+07:00")
        self.assertEqual(result["next_reminder"], "2025-10-25T12:00:00+07:00")
        self.assertEqual(result["owner"], self.user.pk)
        self.assertEqual(result["linked_habit"], None)

    def test_habit_retrieve_403(self):
        """Тест на доступ только к своим привычкам."""
        other_user = User.objects.create(email="other@example.com")
        other_habit = Habit.objects.create(
            owner=other_user,
            place="На улице",
            time=datetime.time(hour=12),
            action="Пробежать километр",
            is_pleasant=False,
            is_good=True,
            frequency=3,
            reward="Cъесть конфету",
            continuation_time=5,
            is_public=False,
        )

        url = reverse_lazy("habits:habit_retrieve", args=(other_habit.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_habit_list(self):
        """Тест на вывод своих привычек."""
        url = reverse_lazy("habits:habits_list")
        response = self.client.get(url)
        result = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["next"], None)
        self.assertEqual(result["previous"], None)
        self.assertEqual(len(result["results"]), 2)

    def test_habit_public_list(self):
        """Тест вывода публичных привычек."""
        url = reverse_lazy("habits:public_habits_list")
        response = self.client.get(url)
        result = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["results"][0]["id"], self.public_habit.pk)
        self.assertEqual(result["results"][0]["is_public"], True)

    def test_habit_public_test_superuser(self):
        """Тест вывода всех привычек для суперюзера."""
        self.client.force_authenticate(user=self.superuser)
        url = reverse_lazy("habits:public_habits_list")
        response = self.client.get(url)
        result = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result["count"], 3)
        self.assertEqual(len(result["results"]), 3)

        habit_ids = [item["id"] for item in result["results"]]
        self.assertIn(self.habit.pk, habit_ids)
        self.assertIn(self.public_habit.pk, habit_ids)
        self.assertIn(self.private_habit.pk, habit_ids)
