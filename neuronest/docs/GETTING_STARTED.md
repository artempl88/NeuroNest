# 🚀 NeuroNest - Руководство по началу работы

## 📋 Описание проекта

NeuroNest - это эксклюзивный Telegram Mini-App маркетплейс AI агентов с NFT-доступом и оплатой в криптовалюте NOTPUNKS. 

### 🎯 Ключевые особенности

- 🎮 **NFT-гейт система**: Доступ только для владельцев NOT Punks NFT
- 💎 **Крипто платежи**: Оплата в NOTPUNKS jetton токенах 
- 🤖 **AI агенты**: 20+ готовых агентов в различных категориях
- ⚡ **Real-time**: Мониторинг выполнения в реальном времени
- 🔒 **Безопасность**: Изолированное выполнение в Docker

## 🏗 Архитектура проекта

```
neuronest/
├── 📱 frontend/          # Next.js Telegram Mini-App
│   ├── src/
│   │   ├── app/          # App Router (Next.js 14)
│   │   ├── components/   # React компоненты
│   │   ├── hooks/        # Custom hooks
│   │   └── utils/        # Утилиты
│   ├── package.json
│   └── tailwind.config.js
│
├── 🖥 backend/           # FastAPI REST API
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Конфигурация
│   │   ├── models/       # SQLAlchemy модели
│   │   ├── services/     # Бизнес логика
│   │   └── middleware/   # Middleware
│   ├── requirements.txt
│   └── Dockerfile
│
├── 🤖 agents/            # AI агенты
│   ├── wrappers/         # Python обёртки
│   ├── config/           # Конфигурации
│   └── docker/           # Docker images
│
├── 🐳 docker/            # Docker конфигурации
│   ├── nginx/
│   ├── prometheus/
│   └── grafana/
│
└── 📄 docs/              # Документация
```

## 🛠 Технический стек

### Frontend
- **Next.js 14** с App Router
- **TypeScript** для типизации
- **TailwindCSS** + **Framer Motion** для UI/UX
- **TON Connect SDK** для кошелька
- **Telegram Mini App SDK**

### Backend
- **Python 3.11** + **FastAPI**
- **PostgreSQL** + **SQLAlchemy**
- **Redis** для кэширования
- **Celery** для фоновых задач
- **Docker** для изоляции агентов

### Blockchain
- **TON** блокчейн
- **NOTPUNKS** jetton токены
- **NFT** коллекции для доступа

## 🚀 Быстрый старт

### 1. Предварительные требования

Убедитесь, что у вас установлено:

```bash
# Основные зависимости
- Node.js 18+ 
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

# Для разработки
- Git
- VS Code (рекомендуется)
```

### 2. Клонирование и настройка

```bash
# Клонируем репозиторий
git clone https://github.com/neuronest/neuronest.git
cd neuronest

# Копируем environment файлы
cp .env.example .env
cp frontend/.env.local.example frontend/.env.local

# Редактируем настройки
nano .env
```

### 3. Настройка переменных окружения

Основные переменные в `.env`:

```bash
# База данных
DATABASE_URL=postgresql://neuronest:password@localhost:5432/neuronest_db
REDIS_URL=redis://localhost:6379/0

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_BOT_USERNAME=neuronest_bot

# TON Blockchain  
TON_NETWORK=testnet
TON_API_KEY=your_ton_api_key

# NFT Collections
NOT_PUNKS_COLLECTION=EQAA...
NOT_PUNKS_GIRLS_COLLECTION=EQBB...
TNO_ELEMENTAL_KIDS_COLLECTION=EQCC...

# NOTPUNKS Jetton
NOTPUNKS_JETTON_MASTER=EQDD...

# Security
SECRET_KEY=your-super-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
ENCRYPTION_KEY=your-32-byte-encryption-key
```

### 4. Запуск с Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f backend
```

### 5. Запуск в режиме разработки

#### Backend:
```bash
cd backend

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt

# Запуск миграций
alembic upgrade head

# Запуск сервера
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend:
```bash
cd frontend

# Установка зависимостей
npm install

# Запуск dev сервера
npm run dev
```

#### Celery Worker:
```bash
cd backend
celery -A app.celery worker --loglevel=info
```

## 🔧 Разработка

### Добавление нового AI агента

1. **Создайте Docker image агента:**
```bash
cd agents/
mkdir my-new-agent
cd my-new-agent

# Создайте Dockerfile и код агента
# Пример структуры:
# ├── Dockerfile
# ├── main.py
# ├── requirements.txt
# └── config.json
```

2. **Добавьте агента в базу данных:**
```python
# В backend/app/core/database.py добавьте в create_demo_agents()
{
    "name": "my_new_agent",
    "display_name": "🔥 My New Agent",
    "description": "Описание агента",
    "category": AgentCategory.PRODUCTIVITY,
    "base_price": 2 * (10 ** 9),  # 2 NOTPUNKS
    "docker_image": "neuronest/my-new-agent",
    "input_schema": {...},
    "required_apis": ["openai"],
    "author": "Your Name"
}
```

3. **Создайте UI компонент:**
```typescript
// В frontend/src/components/agents/
export function MyNewAgentCard() {
  // Компонент карточки агента
}
```

### Структура API

#### Основные endpoints:

```
GET    /api/v1/health              # Health check
POST   /api/v1/auth/telegram       # Telegram auth
GET    /api/v1/user/profile        # Профиль пользователя
GET    /api/v1/agents              # Список агентов
POST   /api/v1/agents/{id}/execute # Запуск агента
GET    /api/v1/executions          # История выполнений
WebSocket /ws/executions/{id}      # Real-time статус
```

### База данных

#### Основные таблицы:
- `users` - Пользователи
- `agents` - AI агенты  
- `agent_executions` - Выполнения агентов
- `transactions` - Транзакции

#### Миграции:
```bash
# Создание миграции
alembic revision --autogenerate -m "Add new table"

# Применение миграций
alembic upgrade head

# Откат миграции
alembic downgrade -1
```

## 🧪 Тестирование

### Backend тесты:
```bash
cd backend

# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=app --cov-report=html

# Запуск конкретного теста
pytest tests/test_agents.py::test_agent_execution
```

### Frontend тесты:
```bash
cd frontend

# Запуск тестов
npm test

# Запуск с покрытием
npm run test:coverage

# Запуск в watch режиме
npm run test:watch
```

## 📈 Мониторинг

### Доступные дашборды:

- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **FastAPI Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000

### Логи:
```bash
# Backend логи
docker-compose logs -f backend

# Celery worker логи  
docker-compose logs -f celery_worker

# База данных логи
docker-compose logs -f postgres
```

## 🚀 Деплой в Production

### 1. Подготовка:
```bash
# Сборка Docker images
docker-compose -f docker-compose.prod.yml build

# Проверка конфигурации
docker-compose -f docker-compose.prod.yml config
```

### 2. Переменные для production:
```bash
# Обновите .env для production
NODE_ENV=production
DEBUG=false
CORS_ORIGINS=["https://yourdomain.com"]
```

### 3. Запуск:
```bash
# Запуск в production режиме
docker-compose -f docker-compose.prod.yml up -d

# Проверка
curl https://yourdomain.com/api/v1/health
```

## 🔧 Troubleshooting

### Частые проблемы:

#### 1. База данных не подключается:
```bash
# Проверьте статус PostgreSQL
docker-compose ps postgres

# Проверьте логи
docker-compose logs postgres

# Пересоздайте том
docker-compose down -v
docker-compose up -d postgres
```

#### 2. Celery worker не работает:
```bash
# Проверьте Redis подключение
redis-cli ping

# Перезапустите worker
docker-compose restart celery_worker
```

#### 3. Frontend не подключается к API:
```bash
# Проверьте CORS настройки
# Убедитесь что API_URL правильный в .env.local
```

## 📞 Поддержка

- **GitHub Issues**: [Создать issue](https://github.com/neuronest/neuronest/issues)
- **Telegram**: @neuronest_support
- **Email**: support@neuronest.ai

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Создайте Pull Request

## 📄 Лицензия

MIT License - смотрите [LICENSE](../LICENSE) для деталей.

---

**Готово к запуску! 🚀**

Теперь у вас есть полноценный Telegram Mini-App маркетплейс AI агентов с NFT-доступом! 