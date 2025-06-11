#!/bin/bash
set -e

# Функция для ожидания доступности сервиса
wait_for_service() {
    local host=$1
    local port=$2
    local service=$3
    
    echo "Ожидание $service..."
    while ! nc -z $host $port 2>/dev/null; do
        echo "  $service недоступен - ожидание..."
        sleep 1
    done
    echo "✅ $service доступен"
}

# Извлекаем хост и порт из DATABASE_URL
if [[ $DATABASE_URL =~ @([^:]+):([0-9]+)/ ]]; then
    DB_HOST="${BASH_REMATCH[1]}"
    DB_PORT="${BASH_REMATCH[2]}"
    wait_for_service $DB_HOST $DB_PORT "PostgreSQL"
fi

# Извлекаем хост и порт из REDIS_URL
if [[ $REDIS_URL =~ redis://([^:]+):([0-9]+) ]]; then
    REDIS_HOST="${BASH_REMATCH[1]}"
    REDIS_PORT="${BASH_REMATCH[2]}"
    wait_for_service $REDIS_HOST $REDIS_PORT "Redis"
fi

# Запускаем миграции
echo "Запуск миграций базы данных..."
alembic upgrade head

echo "✅ Инициализация завершена"

# Запускаем приложение
echo "Запуск приложения..."
exec "$@" 