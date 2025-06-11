"""
Middleware для ограничения количества запросов
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware для rate limiting"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(deque)
    
    async def dispatch(self, request: Request, call_next):
        # Получаем IP адрес клиента
        client_ip = request.client.host
        
        # Текущее время
        now = time.time()
        minute_ago = now - 60
        
        # Удаляем старые записи
        while self.requests[client_ip] and self.requests[client_ip][0] < minute_ago:
            self.requests[client_ip].popleft()
        
        # Проверяем лимит
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(status_code=429, detail="Too many requests")
        
        # Добавляем текущий запрос
        self.requests[client_ip].append(now)
        
        response = await call_next(request)
        return response 