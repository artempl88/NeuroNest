"""
Middleware для аутентификации
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware для проверки аутентификации"""
    
    # Пути, не требующие аутентификации
    PUBLIC_PATHS = [
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/telegram/verify"
    ]
    
    async def dispatch(self, request: Request, call_next):
        # Пропускаем публичные пути
        if any(request.url.path.startswith(path) for path in self.PUBLIC_PATHS):
            return await call_next(request)
        
        # TODO: Добавить проверку JWT токена из заголовка Authorization
        # Пока просто пропускаем все запросы
        
        response = await call_next(request)
        return response 