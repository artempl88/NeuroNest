"""
Настройка логирования для NeuroNest
"""

import logging
import sys
from app.core.config import settings

def setup_logging():
    """Настройка логирования приложения"""
    
    # Определяем уровень логирования
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Настройка формата
    if settings.LOG_FORMAT == "json":
        import json
        
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_obj = {
                    'timestamp': self.formatTime(record, self.datefmt),
                    'level': record.levelname,
                    'logger': record.name,
                    'message': record.getMessage(),
                    'pathname': record.pathname,
                    'line': record.lineno
                }
                if record.exc_info:
                    log_obj['exception'] = self.formatException(record.exc_info)
                return json.dumps(log_obj)
        
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Настройка обработчиков
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    # Настройка корневого логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)
    
    # Отключаем дублирование логов
    root_logger.propagate = False
    
    # Настройка уровней для сторонних библиотек
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING) 