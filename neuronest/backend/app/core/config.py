"""
Конфигурация NeuroNest Backend
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # =============================================================================
    # ОСНОВНЫЕ НАСТРОЙКИ
    # =============================================================================
    APP_NAME: str = Field(default="NeuroNest", description="Название приложения")
    APP_VERSION: str = Field(default="1.0.0", description="Версия приложения")
    DEBUG: bool = Field(default=False, description="Режим отладки")
    
    # =============================================================================
    # БАЗА ДАННЫХ
    # =============================================================================
    DATABASE_URL: str = Field(..., description="URL подключения к PostgreSQL")
    DB_POOL_SIZE: int = Field(default=20, description="Размер пула соединений")
    DB_MAX_OVERFLOW: int = Field(default=30, description="Максимальное переполнение пула")
    DB_POOL_TIMEOUT: int = Field(default=30, description="Таймаут пула соединений")
    
    # =============================================================================
    # REDIS
    # =============================================================================
    REDIS_URL: str = Field(..., description="URL подключения к Redis")
    
    # =============================================================================
    # БЕЗОПАСНОСТЬ
    # =============================================================================
    SECRET_KEY: str = Field(..., description="Секретный ключ приложения")
    JWT_SECRET_KEY: str = Field(..., description="Секретный ключ для JWT")
    JWT_ALGORITHM: str = Field(default="HS256", description="Алгоритм JWT")
    JWT_EXPIRATION_HOURS: int = Field(default=24, description="Срок действия JWT в часах")
    
    ENCRYPTION_KEY: str = Field(..., description="Ключ шифрования")
    FERNET_KEY: str = Field(..., description="Ключ Fernet для шифрования")
    
    # =============================================================================
    # TELEGRAM BOT
    # =============================================================================
    TELEGRAM_BOT_TOKEN: str = Field(..., description="Токен Telegram бота")
    TELEGRAM_BOT_USERNAME: str = Field(..., description="Username Telegram бота")
    TELEGRAM_WEBHOOK_URL: Optional[str] = Field(default=None, description="URL webhook")
    TELEGRAM_SECRET_TOKEN: Optional[str] = Field(default=None, description="Секретный токен webhook")
    
    # =============================================================================
    # TON BLOCKCHAIN
    # =============================================================================
    TON_NETWORK: str = Field(default="testnet", description="Сеть TON (testnet/mainnet)")
    TON_API_ENDPOINT: str = Field(..., description="Endpoint TON API")
    TON_API_KEY: str = Field(..., description="Ключ TON API")
    
    # NFT коллекции для контроля доступа
    NOT_PUNKS_COLLECTION: str = Field(..., description="Адрес коллекции NOT Punks")
    NOT_PUNKS_GIRLS_COLLECTION: str = Field(..., description="Адрес коллекции NOT Punks Girls")
    TNO_ELEMENTAL_KIDS_COLLECTION: str = Field(..., description="Адрес коллекции TNO Elemental Kids")
    
    # NOTPUNKS Jetton
    NOTPUNKS_JETTON_MASTER: str = Field(..., description="Адрес мастер-контракта NOTPUNKS jetton")
    NOTPUNKS_JETTON_DECIMAL: int = Field(default=9, description="Десятичные знаки NOTPUNKS jetton")
    
    # =============================================================================
    # RATE LIMITING
    # =============================================================================
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(default=60, description="Лимит запросов в минуту")
    RATE_LIMIT_BURST: int = Field(default=10, description="Burst лимит")
    RATE_LIMIT_PREMIUM_MULTIPLIER: int = Field(default=5, description="Множитель для премиум пользователей")
    
    # =============================================================================
    # AI АГЕНТЫ
    # =============================================================================
    AGENTS_DOCKER_REGISTRY: str = Field(default="neuronest/agents", description="Docker registry для агентов")
    AGENTS_EXECUTION_TIMEOUT: int = Field(default=300, description="Таймаут выполнения агентов в секундах")
    AGENTS_MAX_CONCURRENT: int = Field(default=10, description="Максимальное количество одновременных агентов")
    AGENTS_CLEANUP_AFTER_HOURS: int = Field(default=24, description="Время жизни результатов в часах")
    
    # API ключи по умолчанию (пользователи могут переопределить)
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API ключ")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, description="Anthropic API ключ")
    GOOGLE_AI_API_KEY: Optional[str] = Field(default=None, description="Google AI API ключ")
    COHERE_API_KEY: Optional[str] = Field(default=None, description="Cohere API ключ")
    
    # =============================================================================
    # ПЛАТЕЖИ
    # =============================================================================
    PAYMENT_CONFIRMATION_BLOCKS: int = Field(default=3, description="Количество блоков для подтверждения платежа")
    PAYMENT_TIMEOUT_MINUTES: int = Field(default=15, description="Таймаут платежа в минутах")
    COMMISSION_RATE: float = Field(default=0.07, description="Комиссия платформы (7%)")
    PREMIUM_COMMISSION_RATE: float = Field(default=0.03, description="Комиссия для премиум пользователей (3%)")
    
    # =============================================================================
    # DOCKER
    # =============================================================================
    DOCKER_NETWORK: str = Field(default="neuronest_network", description="Сеть Docker")
    DOCKER_AGENTS_SUBNET: str = Field(default="172.20.0.0/16", description="Подсеть для агентов")
    DOCKER_RESOURCE_LIMITS_MEMORY: str = Field(default="512m", description="Лимит памяти для контейнеров")
    DOCKER_RESOURCE_LIMITS_CPU: str = Field(default="0.5", description="Лимит CPU для контейнеров")
    
    # =============================================================================
    # ЛОГИРОВАНИЕ И МОНИТОРИНГ
    # =============================================================================
    LOG_LEVEL: str = Field(default="INFO", description="Уровень логирования")
    LOG_FORMAT: str = Field(default="json", description="Формат логов")
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN для отслеживания ошибок")
    
    PROMETHEUS_ENABLED: bool = Field(default=True, description="Включить Prometheus метрики")
    PROMETHEUS_PORT: int = Field(default=9090, description="Порт Prometheus")
    
    # =============================================================================
    # HTTP/CORS
    # =============================================================================
    CORS_ORIGINS: List[str] = Field(default=["*"], description="Разрешенные домены для CORS")
    ALLOWED_HOSTS: List[str] = Field(default=["*"], description="Разрешенные хосты")
    
    # =============================================================================
    # DEVELOPMENT НАСТРОЙКИ
    # =============================================================================
    DEV_SKIP_NFT_CHECK: bool = Field(default=False, description="Пропустить проверку NFT в dev режиме")
    DEV_MOCK_PAYMENTS: bool = Field(default=False, description="Использовать моки для платежей")
    DEV_ENABLE_DEBUG_UI: bool = Field(default=False, description="Включить debug UI")
    DEV_ALLOW_CORS_ALL: bool = Field(default=False, description="Разрешить CORS для всех доменов")
    
    @validator('CORS_ORIGINS', pre=True)
    def parse_cors_origins(cls, v):
        """Парсинг CORS origins из строки"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('ALLOWED_HOSTS', pre=True)
    def parse_allowed_hosts(cls, v):
        """Парсинг allowed hosts из строки"""
        if isinstance(v, str):
            return [host.strip() for host in v.split(',')]
        return v
    
    @property
    def nft_collections(self) -> List[str]:
        """Получить список всех NFT коллекций для проверки доступа"""
        return [
            self.NOT_PUNKS_COLLECTION,
            self.NOT_PUNKS_GIRLS_COLLECTION,
            self.TNO_ELEMENTAL_KIDS_COLLECTION
        ]
    
    @property
    def database_config(self) -> dict:
        """Конфигурация базы данных"""
        return {
            "url": self.DATABASE_URL,
            "pool_size": self.DB_POOL_SIZE,
            "max_overflow": self.DB_MAX_OVERFLOW,
            "pool_timeout": self.DB_POOL_TIMEOUT
        }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Создание экземпляра настроек
settings = Settings() 