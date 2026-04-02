# 🛠 Helpdesk Chat Platform

**Helpdesk Chat Platform** — это полноценная система поддержки пользователей с возможностью создания заявок (тикетов) и общения с поддержкой в реальном времени через WebSocket.

Проект демонстрирует работу с production-стеком:  
**Django + DRF + Channels + PostgreSQL + Redis + Docker + Nginx**

---

## 🚀 Основные возможности

- 🔐 JWT-аутентификация (access + refresh)
- 🎫 CRUD заявок (тикетов)
- 👥 Role-based access control (RBAC)
- 💬 WebSocket чат в реальном времени
- ⌨️ Индикатор «печатает...»
- 🗂 История сообщений
- 🔒 Проверка доступа к чат-комнатам
- 📄 Swagger / OpenAPI документация
- 🐳 Полностью dockerized проект

---

## 🧠 Архитектура проекта

```
Client (HTTP / WebSocket)
        ↓
Django REST API (Views / Serializers)
        ↓
Business Logic (Serializers / Models)
        ↓
Database (PostgreSQL)

WebSocket Flow:
Client → Channels → Consumer → Redis → Broadcast
```

### 🔹 Принципы

- Разделение HTTP и WebSocket логики  
- Валидация через сериализаторы  
- Контроль доступа:
  - API  
  - WebSocket (Consumers)  
- Минимальная бизнес-логика во views  

---

## 🧱 Структура проекта

```
PetProjectSupport/
│
├── helpdesk/
│   ├── settings.py
│   ├── settings_prod.py
│   ├── asgi.py
│   └── urls.py
│
├── support/
│   ├── models.py
│   ├── serializers.py
│   ├── consumers.py
│   ├── views.py
│   └── migrations/
│
├── docker/
├── nginx/
├── docker-compose.yml
└── .env
```

---

## 👥 Роли и доступ

| Роль     | Возможности |
|----------|------------|
| User     | Создаёт заявки, пишет только в свои |
| Support  | Видит все заявки, отвечает |
| Admin    | Полный доступ |

### 🔐 Контроль доступа

- Пользователь → только свои заявки  
- Support/Admin → все заявки  
- Проверка доступа реализована:
  - в сериализаторах  
  - в WebSocket Consumer  

---

## 🎫 Логика заявок

### Статусы

- `new` — новая  
- `in_progress` — в работе  
- `closed` — закрыта  

### Особенности

- `updated_at` обновляется при изменении  
- сортировка по `created_at`  
- связь через `UserProfile`  

---

## 💬 WebSocket чат

### 📡 Подключение

```
ws://127.0.0.1/ws/chat/{room_id}/?token={access_token}
```

- `room_id` — ID заявки  
- `token` — JWT access token  

---

### 📩 Сообщение

```json
{
  "message": "Привет, нужна помощь"
}
```

---

### ⌨️ Typing indicator

```json
{ "type": "typing", "status": "start" }
{ "type": "typing", "status": "stop" }
```

---

### 🔐 Безопасность WebSocket

- Проверка авторизации  
- Проверка доступа к заявке  
- Broadcast через Redis  
- Исключение отправителя из событий typing  

---

## 🔒 Безопасность

- JWT (SimpleJWT)  
- Refresh токен хранится в httpOnly cookie  
- Проверка прав доступа  
- Валидация пользователя  
- Ограничение доступа к чатам  

---

## 🧰 Технологии

| Технология | Назначение |
|---|---|
| Python 3.11 | Язык |
| Django | Backend |
| Django REST Framework | API |
| Django Channels | WebSocket |
| PostgreSQL | БД |
| Redis | Channel layer |
| JWT | Аутентификация |
| Daphne | ASGI сервер |
| Nginx | Reverse proxy |
| Docker | Контейнеризация |
| Poetry | Зависимости |

---

## 📦 Запуск

### 🐳 Docker (рекомендуется)

```bash
git clone <repo>
cd PetProjectSupport
cp .env.example .env
docker-compose up --build
```

Открыть в браузере:

```
http://127.0.0.1
```

---

### 💻 Локально

```bash
pip install poetry
poetry install
poetry run python manage.py migrate
poetry run daphne -b 127.0.0.1 -p 8000 helpdesk.asgi:application
```

---

## 👤 Создание суперпользователя

Docker:

```bash
docker exec -it helpdesk_web python manage.py createsuperuser
```

Локально:

```bash
poetry run python manage.py createsuperuser
```

---

## 📚 API

### Swagger UI

```
http://127.0.0.1/api/schema/swagger-ui/
```

### OpenAPI

```
http://127.0.0.1/api/schema/
```

---

### Основные эндпоинты

| Метод | Endpoint | Описание |
|------|----------|----------|
| POST | /api/register/ | Регистрация |
| POST | /api/login/ | Вход |
| GET | /api/requests/ | Список заявок |
| POST | /api/requests/ | Создать заявку |
| GET | /api/requests/{id}/ | Детали заявки |
| GET | /api/requests/{id}/messages/ | Сообщения |
| POST | /api/requests/{id}/messages/ | Отправка сообщения |
| POST | /api/token/refresh/ | Обновление токена |
| POST | /api/logout/ | Выход |

---

## 🧪 Тестирование

Локально:

```bash
poetry run pytest
```

Docker:

```bash
docker exec -it helpdesk_web pytest
```

---

## 💡 Особенности реализации

- Role-based доступ через `UserProfile`  
- Property `is_support` для проверки роли  
- Валидация доступа в сериализаторах  
- Проверка прав в WebSocket Consumer  
- Broadcast сообщений через Redis  
- Lazy создание профиля пользователя  
- Автоматическое обновление `updated_at`  

---

## 📈 Что демонстрирует проект

- Django backend разработка  
- WebSocket (real-time системы)  
- REST API проектирование  
- Docker + Nginx инфраструктура  
- Работа с Redis  
- Безопасность (JWT, permissions)  

---

## 🚀 Roadmap

- Уведомления (email / websocket)  
- Pagination сообщений  
- Поддержка файлов (attachments)  
- Rate limiting  
- CI/CD  
- Monitoring (Prometheus / Grafana)  

---

## 🤝 Contributing

Pull Request и Issues приветствуются 🚀  

---

## 📄 License

MIT  

---

## 💼 Для работодателя

Проект демонстрирует:

- опыт разработки на Django  
- работу с WebSocket (Channels)  
- понимание архитектуры backend-сервисов  
- навыки работы с Docker и инфраструктурой  
- реализацию безопасной аутентификации  