"""
Конфигурация базы данных NeuroNest
"""

from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging
from typing import Generator

from app.core.config import settings

logger = logging.getLogger(__name__)

# Метаданные для именования ограничений
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)

# Базовый класс для моделей
Base = declarative_base(metadata=metadata)

# Создание движка базы данных
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Фабрика сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_database():
    """Dependency для получения сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_database() -> None:
    """Инициализация базы данных"""
    try:
        # Создаем все таблицы
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Таблицы базы данных созданы")
        
        # Создаем начальные данные
        await create_initial_data()
        
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации базы данных: {e}")
        raise


async def create_initial_data() -> None:
    """Создание начальных данных для приложения"""
    db = None
    try:
        db = SessionLocal()
        
        # Проверяем подключение к базе данных
        db.execute(text("SELECT 1"))
        logger.info("✅ Подключение к базе данных установлено")
        
        # Создаем демонстрационных агентов
        create_demo_agents(db)
        
        logger.info("✅ Начальные данные успешно созданы")
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания начальных данных: {e}")
        if db:
            db.rollback()
    finally:
        if db:
            db.close()


def create_demo_agents(db: Session) -> None:
    """Создание демонстрационных AI агентов"""
    from app.models.agent import Agent, AgentCategory, AgentStatus
    
    demo_agents = [
        {
            "name": "Crypto Portfolio Analyzer",
            "description": "Анализирует криптовалютный портфель и предоставляет рекомендации по торговле",
            "category": AgentCategory.FINANCE,
            "price_ton": 5.0,
            "rating": 95,
            "status": AgentStatus.ACTIVE,
            "input_schema": {
                "type": "object",
                "properties": {
                    "wallet_address": {"type": "string", "description": "Адрес кошелька для анализа"},
                    "timeframe": {"type": "string", "enum": ["1d", "7d", "30d"], "default": "7d"}
                },
                "required": ["wallet_address"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "portfolio_value": {"type": "number"},
                    "recommendations": {"type": "array", "items": {"type": "string"}},
                    "risk_score": {"type": "number", "minimum": 0, "maximum": 100}
                }
            }
        },
        {
            "name": "NFT Collection Valuator",
            "description": "Оценивает NFT коллекции и прогнозирует ценовые тренды",
            "category": AgentCategory.FINANCE,
            "price_ton": 3.0,
            "rating": 88,
            "status": AgentStatus.ACTIVE,
            "input_schema": {
                "type": "object",
                "properties": {
                    "collection_address": {"type": "string", "description": "Адрес NFT коллекции"},
                    "analysis_depth": {"type": "string", "enum": ["basic", "advanced"], "default": "basic"}
                },
                "required": ["collection_address"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "floor_price": {"type": "number"},
                    "trend_direction": {"type": "string", "enum": ["up", "down", "stable"]},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                }
            }
        },
        {
            "name": "Smart Contract Auditor",
            "description": "Автоматический анализ и аудит смарт-контрактов на уязвимости",
            "category": AgentCategory.DEVELOPMENT,
            "price_ton": 8.0,
            "rating": 92,
            "status": AgentStatus.ACTIVE,
            "input_schema": {
                "type": "object",
                "properties": {
                    "contract_code": {"type": "string", "description": "Код смарт-контракта"},
                    "audit_level": {"type": "string", "enum": ["basic", "advanced", "comprehensive"], "default": "basic"}
                },
                "required": ["contract_code"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "vulnerabilities": {"type": "array", "items": {"type": "object"}},
                    "security_score": {"type": "number", "minimum": 0, "maximum": 100},
                    "recommendations": {"type": "array", "items": {"type": "string"}}
                }
            }
        }
    ]
    
    # Проверяем, существуют ли уже агенты
    existing_count = db.query(Agent).count()
    if existing_count > 0:
        logger.info(f"Демо-агенты уже существуют ({existing_count} агентов)")
        return
        
    # Создаем новых агентов
    for agent_data in demo_agents:
        try:
            agent = Agent(**agent_data)
            db.add(agent)
            logger.info(f"Создан агент: {agent.name}")
        except Exception as e:
            logger.error(f"Ошибка создания агента {agent_data['name']}: {e}")
    
    db.commit()
    logger.info(f"Создано {len(demo_agents)} демо-агентов")


def create_test_db() -> None:
    """
    Создание тестовой базы данных для юнит-тестов
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Используем SQLite для тестов
    test_engine = create_engine(
        "sqlite:///./test.db",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    
    Base.metadata.create_all(bind=test_engine)
    
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine) 