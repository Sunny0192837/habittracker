# habbittracker

Django REST Framework приложение, настроенное для запуска через Docker Compose.

## Убедитесь, что у вас установлен Docker и Git

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/downloads)

## Быстрый старт

### 1. Клонирование репозитория

```commandline
git clone <your-repository-url>
cd <repository-name>
git checkout feature
```

### 2. Создание .env файла
```commandline
cp .env.example .env
```
Отредактируйте .env файл, указав необходимые значения.

### 3. Запуск
Приложение будет доступно по адресу: http://localhost