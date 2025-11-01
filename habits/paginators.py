from rest_framework.pagination import PageNumberPagination


class HabitPaginator(PageNumberPagination):
    """
    Пагинатор для привычки.
    """

    page_size = 5
