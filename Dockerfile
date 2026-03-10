# Используем официальный Python-образ
FROM python:3.11-slim

# Устанавливаем системные зависимости для psycopg2 и других
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Устанавливаем Poetry
RUN pip install poetry

# Конфигурируем Poetry: не создавать виртуальное окружение (оно не нужно в контейнере)
RUN poetry config virtualenvs.create false

# Устанавливаем зависимости
RUN pip install --upgrade pip setuptools
RUN pip install poetry

# Отключаем создание виртуального окружения
RUN poetry config virtualenvs.create false

# Устанавливаем зависимости с подробным выводом
RUN poetry install --no-interaction --no-ansi -v --no-root

# Копируем весь проект
COPY . .

# Открываем порт 8000
EXPOSE 8000

# Команда запуска: используем daphne для поддержки WebSocket
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "helpdesk.asgi:application"]