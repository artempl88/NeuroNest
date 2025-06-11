"""
NeuroNest Backend API
Telegram Mini-App маркетплейс AI агентов с NFT-доступом
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_database
from app.core.redis import init_redis
from app.core.logging import setup_logging
from app.middleware.auth import AuthMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.api.v1.router import api_router
from app.websocket.router import websocket_router

# Настройка логирования
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    try:
        # Инициализация при запуске
        logger.info("🚀 Запуск NeuroNest Backend...")
        
        # Инициализация базы данных
        init_database()
        logger.info("✅ База данных инициализирована")
        
        # Инициализация Redis
        await init_redis()
        logger.info("✅ Redis подключен")
        
        logger.info("🎉 NeuroNest Backend готов к работе!")
        yield
        
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске: {e}")
        raise
    finally:
        # Очистка при завершении
        logger.info("🔄 Завершение работы NeuroNest Backend...")


def create_app() -> FastAPI:
    """Создание экземпляра FastAPI приложения"""
    
    app = FastAPI(
        title="NeuroNest API",
        description="Telegram Mini-App маркетплейс AI агентов с NFT-доступом",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )

    # Middleware
    setup_middleware(app)
    
    # Маршруты
    setup_routes(app)
    
    return app


def setup_middleware(app: FastAPI):
    """Настройка middleware"""
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted hosts (для production)
    if not settings.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts_list
        )
    
    # Аутентификация
    app.add_middleware(AuthMiddleware)
    
    # Rate limiting
    app.add_middleware(RateLimitMiddleware)


def setup_routes(app: FastAPI):
    """Настройка маршрутов"""
    
    # Health check
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "neuronest-backend"}
    
    # API routes
    app.include_router(api_router, prefix="/api/v1")
    
    # WebSocket routes
    app.include_router(websocket_router, prefix="/ws")
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Необработанная ошибка: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Внутренняя ошибка сервера"}
        )


# Создание приложения
app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_config=None  # Используем наше логирование
    ) 