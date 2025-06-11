# 🧠 NeuroNest by NOT Punks

Telegram Mini-App маркетплейс AI агентов с NFT-доступом и оплатой в криптовалюте.

## 🎯 Особенности

- 🎮 **NFT-Гейт**: Доступ только для владельцев NOT Punks NFT
- 💎 **Крипто-Платежи**: Оплата в NOTPUNKS jetton токенах
- 🤖 **AI Агенты**: Более 20 готовых агентов в различных категориях
- ⚡ **Real-time**: Мониторинг выполнения задач в реальном времени
- 🔒 **Безопасность**: Изолированное выполнение в Docker контейнерах

## 🏗 Архитектура

```
neuronest/
├── frontend/          # Next.js Telegram Mini-App
├── backend/           # FastAPI REST API
├── agents/            # Обёртки для AI агентов
├── docker/            # Docker конфигурации
├── contracts/         # TON smart contracts
└── docs/              # Документация
```

## 🚀 Быстрый старт

### Предварительные требования

- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL
- Redis

### Запуск в development режиме

1. **Клонируйте репозиторий**
```bash
git clone <repo-url>
cd neuronest
```

2. **Настройте environment переменные**
```bash
cp .env.example .env
# Отредактируйте .env файл с вашими настройками
```

3. **Запустите с Docker Compose**
```bash
docker-compose up -d
```

4. **Запустите frontend**
```bash
cd frontend
npm install
npm run dev
```

5. **Запустите backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## 📱 Telegram Mini-App

Приложение доступно по ссылке: `https://t.me/neuronest_bot/app`

## 🛠 Разработка

### Этапы развития

- [x] **Этап 1**: Базовая инфраструктура
- [ ] **Этап 2**: NFT-гейт система
- [ ] **Этап 3**: Интеграция AI агентов
- [ ] **Этап 4**: Платежная система
- [ ] **Этап 5**: Полировка и запуск

### Добавление нового AI агента

1. Создайте обёртку в `agents/wrappers/`
2. Добавьте конфигурацию в `agents/config/`
3. Обновите схему API в `backend/schemas/`
4. Добавьте UI компонент в `frontend/components/agents/`

## 💰 Монетизация

- Комиссия 7% с каждой транзакции
- Premium подписка со сниженными комиссиями
- Приоритетная очередь выполнения

## 🔐 Безопасность

- Изоляция агентов в Docker контейнерах
- Шифрование API ключей пользователей
- Rate limiting для API запросов
- Проверка NFT владения при каждом запросе

## 📄 Лицензия

MIT License - смотрите [LICENSE](LICENSE) файл для деталей.

## 🤝 Вклад в проект

Мы приветствуем вклад сообщества! Смотрите [CONTRIBUTING.md](CONTRIBUTING.md) для руководства.

## 🐛 Баг репорты

Используйте [GitHub Issues](https://github.com/your-repo/issues) для сообщения о багах.

## ⭐ Поддержка

Если проект вам нравится, поставьте звёздочку ⭐️ 