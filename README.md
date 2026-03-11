# Helpdesk Chat Platform

Платформа для поддержки пользователей с возможностью создания заявок и общения в реальном времени через WebSocket. Проект реализован на Django + DRF + Channels с JWT-аутентификацией и развёртыванием в Docker.

## 🚀 Возможности

- Регистрация и аутентификация пользователей (JWT)
- Создание заявок (тикетов) с разными статусами
- Роли: пользователь, поддержка, администратор
- Чат в реальном времени по каждой заявке (WebSocket)
- Индикатор «печатает»
- История сообщений
- REST API с документацией Swagger
- Контейнеризация: Docker + Docker Compose (Django, PostgreSQL, Redis, Nginx)

## 🛠️ Стек технологий

- Python 3.11
- Django 5.2
- Django REST Framework
- Django Channels (WebSocket)
- PostgreSQL, Redis
- JWT (djangorestframework-simplejwt)
- Daphne (ASGI-сервер)
- Nginx
- Docker / Docker Compose
- Poetry (управление зависимостями)

## 📦 Установка и запуск

### Предварительные требования

- Установленные [Docker](https://docs.docker.com/get-docker/) и [Docker Compose](https://docs.docker.com/compose/install/)
- (Опционально) Poetry для локальной разработки

### Запуск в Docker (рекомендуемый способ)

1. Клонируйте репозиторий:
   ```bash
   git clone <url-вашего-репозитория>
   cd PetProjectSupport