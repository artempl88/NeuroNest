"""
Redis конфигурация для NeuroNest
"""

import redis.asyncio as redis
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

redis_client = None

async def init_redis():
    """Инициализация Redis подключения"""
    global redis_client
    try:
        redis_client = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        await redis_client.ping()
        logger.info("✅ Redis подключен")
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к Redis: {e}")
        raise

async def get_redis():
    """Получить Redis клиент"""
    return redis_client

async def close_redis():
    """Закрыть Redis подключение"""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None 