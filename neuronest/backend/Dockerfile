# =============================================================================
# NEURONEST BACKEND DOCKERFILE
# Multi-stage build for production optimization
# =============================================================================

# -----------------------------------------------------------------------------
# Base Python Image
# -----------------------------------------------------------------------------
FROM python:3.11-slim as base

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Создаем пользователя приложения
RUN groupadd -r neuronest && useradd -r -g neuronest neuronest

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    gcc \
    g++ \
    git \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# Dependencies Stage
# -----------------------------------------------------------------------------
FROM base as dependencies

# Устанавливаем Poetry для управления зависимостями
RUN pip install poetry==1.7.1

# Конфигурируем Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Копируем файлы зависимостей
WORKDIR /app
COPY requirements.txt ./

# Создаем виртуальное окружение и устанавливаем зависимости
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Устанавливаем зависимости
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# -----------------------------------------------------------------------------
# Development Stage
# -----------------------------------------------------------------------------
FROM dependencies as development

# Копируем исходный код
COPY . .

# Устанавливаем права на файлы
RUN chown -R neuronest:neuronest /app

# Создаем необходимые директории
RUN mkdir -p /app/logs /app/uploads /app/temp && \
    chown -R neuronest:neuronest /app/logs /app/uploads /app/temp

USER neuronest

# Порт приложения
EXPOSE 8000

# Команда запуска для разработки
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# -----------------------------------------------------------------------------
# Production Stage
# -----------------------------------------------------------------------------
FROM base as production

# Устанавливаем только production зависимости
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем виртуальное окружение из dependencies stage
COPY --from=dependencies /app/venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Создаем рабочую директорию
WORKDIR /app

# Копируем исходный код
COPY --chown=neuronest:neuronest . .

# Создаем необходимые директории
RUN mkdir -p /app/logs /app/uploads /app/temp && \
    chown -R neuronest:neuronest /app

# Устанавливаем права
RUN chmod +x /app/scripts/entrypoint.sh

USER neuronest

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Порт приложения
EXPOSE 8000

# Entrypoint script
ENTRYPOINT ["/app/scripts/entrypoint.sh"]

# Команда запуска для production
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]

# -----------------------------------------------------------------------------
# Worker Stage (for Celery workers)
# -----------------------------------------------------------------------------
FROM production as worker

# Команда запуска для Celery worker
CMD ["celery", "-A", "app.celery", "worker", "--loglevel=info", "--concurrency=4"]

# -----------------------------------------------------------------------------
# Beat Stage (for Celery beat scheduler)
# -----------------------------------------------------------------------------
FROM production as beat

# Команда запуска для Celery beat
CMD ["celery", "-A", "app.celery", "beat", "--loglevel=info"]

# -----------------------------------------------------------------------------
# Migration Stage (for database migrations)
# -----------------------------------------------------------------------------
FROM production as migration

USER root

# Устанавливаем дополнительные утилиты для миграций
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

USER neuronest

# Команда для запуска миграций
CMD ["alembic", "upgrade", "head"] 