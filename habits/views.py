from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from habits.models import Habit
from habits.paginators import HabitPaginator
from habits.permissions import IsOwner
from habits.serializers import HabitSerializer


class HabitCreateAPIView(generics.CreateAPIView):
    """
    Представление создания привычки.
    """

    serializer_class = HabitSerializer

    def perform_create(self, serializer):
        """Присваивание создателя привычке."""
        serializer.save(owner=self.request.user)


class HabitListAPIView(generics.ListAPIView):
    """
    Представление списка привычек пользователя.
    """

    serializer_class = HabitSerializer
    pagination_class = HabitPaginator

    def get_queryset(self):
        """Фильтрация привычек по владельцу."""
        queryset = Habit.objects.all()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(owner=self.request.user)
        return queryset


class PublicHabitListAPIView(generics.ListAPIView):
    """
    Представление списка привычек пользователя.
    """

    serializer_class = HabitSerializer
    pagination_class = HabitPaginator

    def get_queryset(self):
        """Фильтрация публичных привычек"""
        queryset = Habit.objects.filter(is_public=True)
        if self.request.user.is_superuser:
            queryset = Habit.objects.all()
        return queryset


class HabitRetrieveAPIView(generics.RetrieveAPIView):
    """
    Представление получения привычки.
    """

    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]


class HabitUpdateAPIView(generics.UpdateAPIView):
    """
    Представление обновления урока.
    """

    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]


class HabitDestroyAPIView(generics.DestroyAPIView):
    """
    Представление обновления урока.
    """

    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]
