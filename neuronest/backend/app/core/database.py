"""
Конфигурация базы данных NeuroNest
"""

from sqlalchemy import create_engine, MetaData
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

# Конфигурация движка базы данных
engine_kwargs = {
    "echo": settings.DEBUG,
    "pool_pre_ping": True,
    "pool_recycle": 3600,
}

# Для PostgreSQL добавляем настройки пула соединений
if settings.DATABASE_URL.startswith("postgresql"):
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_timeout": settings.DB_POOL_TIMEOUT,
    })

# Создание движка
engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

# Фабрика сессий
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency для получения сессии базы данных в FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


async def init_db() -> None:
    """
    Инициализация базы данных
    Создает таблицы и выполняет начальную настройку
    """
    try:
        logger.info("🔄 Инициализация базы данных...")
        
        # Импортируем все модели для их регистрации
        from app.models.user import User
        from app.models.agent import Agent, AgentExecution
        from app.models.transaction import Transaction
        
        # Создаем таблицы
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Таблицы базы данных созданы")
        
        # Выполняем начальную настройку
        await create_initial_data()
        
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации базы данных: {e}")
        raise


async def create_initial_data() -> None:
    """
    Создание начальных данных в базе данных
    """
    try:
        db = SessionLocal()
        
        # Проверяем, есть ли уже агенты в базе
        from app.models.agent import Agent, AgentCategory
        
        existing_agents = db.query(Agent).first()
        if not existing_agents:
            logger.info("🤖 Создание демо агентов...")
            await create_demo_agents(db)
        
        db.commit()
        db.close()
        
    except Exception as e:
        logger.error(f"Ошибка создания начальных данных: {e}")
        if db:
            db.rollback()
            db.close()
        raise


async def create_demo_agents(db: Session) -> None:
    """
    Создание демонстрационных AI агентов
    """
    from app.models.agent import Agent, AgentCategory, AgentStatus
    
    demo_agents = [
        {
            "name": "crypto_analyzer",
            "display_name": "💰 Crypto Portfolio Analyzer",
            "description": "Анализирует криптовалютный портфель и дает рекомендации по торговле",
            "short_description": "AI помощник для анализа крипто-портфеля и торговых стратегий",
            "category": AgentCategory.FINANCE,
            "tags": ["crypto", "portfolio", "trading", "analysis"],
            "base_price": 5 * (10 ** 9),  # 5 NOTPUNKS
            "docker_image": "neuronest/crypto-analyzer",
            "input_schema": {
                "type": "object",
                "properties": {
                    "portfolio": {"type": "string", "description": "Портфель в формате JSON"},
                    "risk_level": {"type": "string", "enum": ["low", "medium", "high"], "default": "medium"}
                },
                "required": ["portfolio"]
            },
            "required_apis": ["coingecko"],
            "author": "NeuroNest Team",
            "is_featured": True
        },
        {
            "name": "nft_valuator",
            "display_name": "🎨 NFT Collection Valuator",
            "description": "Оценивает стоимость NFT коллекций и предсказывает ценовые тренды",
            "short_description": "AI оценщик NFT с прогнозированием цен",
            "category": AgentCategory.FINANCE,
            "tags": ["nft", "valuation", "trends", "opensea"],
            "base_price": 3 * (10 ** 9),  # 3 NOTPUNKS
            "docker_image": "neuronest/nft-valuator",
            "input_schema": {
                "type": "object",
                "properties": {
                    "collection_address": {"type": "string", "description": "Адрес NFT коллекции"},
                    "blockchain": {"type": "string", "enum": ["ethereum", "polygon", "ton"], "default": "ethereum"}
                },
                "required": ["collection_address"]
            },
            "required_apis": ["opensea", "alchemy"],
            "author": "NeuroNest Team",
            "is_featured": True
        },
        {
            "name": "code_reviewer",
            "display_name": "👨‍💻 AI Code Reviewer",
            "description": "Проводит детальный анализ кода и предлагает улучшения",
            "short_description": "Автоматический ревьювер кода с рекомендациями",
            "category": AgentCategory.PRODUCTIVITY,
            "tags": ["code", "review", "analysis", "quality"],
            "base_price": 2 * (10 ** 9),  # 2 NOTPUNKS
            "docker_image": "neuronest/code-reviewer",
            "input_schema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Код для анализа"},
                    "language": {"type": "string", "description": "Язык программирования"},
                    "focus": {"type": "string", "enum": ["security", "performance", "style", "all"], "default": "all"}
                },
                "required": ["code", "language"]
            },
            "required_apis": ["openai"],
            "author": "NeuroNest Team"
        },
        {
            "name": "market_researcher",
            "display_name": "📊 Market Research Assistant",
            "description": "Проводит маркетинговые исследования и анализ конкурентов",
            "short_description": "AI ассистент для маркетинговых исследований",
            "category": AgentCategory.BUSINESS,
            "tags": ["market", "research", "competitors", "analysis"],
            "base_price": 7 * (10 ** 9),  # 7 NOTPUNKS
            "docker_image": "neuronest/market-researcher",
            "input_schema": {
                "type": "object",
                "properties": {
                    "industry": {"type": "string", "description": "Отрасль для исследования"},
                    "region": {"type": "string", "description": "Географический регион"},
                    "depth": {"type": "string", "enum": ["basic", "detailed", "comprehensive"], "default": "detailed"}
                },
                "required": ["industry"]
            },
            "required_apis": ["google", "serpapi"],
            "author": "NeuroNest Team"
        },
        {
            "name": "health_advisor",
            "display_name": "🏥 Personal Health Advisor",
            "description": "Персональный консультант по здоровью на основе симптомов и истории",
            "short_description": "AI консультант по вопросам здоровья",
            "category": AgentCategory.HEALTH,
            "tags": ["health", "symptoms", "advice", "wellness"],
            "base_price": 4 * (10 ** 9),  # 4 NOTPUNKS
            "docker_image": "neuronest/health-advisor",
            "input_schema": {
                "type": "object",
                "properties": {
                    "symptoms": {"type": "string", "description": "Описание симптомов"},
                    "age": {"type": "integer", "minimum": 1, "maximum": 120},
                    "gender": {"type": "string", "enum": ["male", "female", "other"]},
                    "medical_history": {"type": "string", "description": "Медицинская история"}
                },
                "required": ["symptoms"]
            },
            "required_apis": ["openai"],
            "author": "NeuroNest Team"
        },
        {
            "name": "game_strategy",
            "display_name": "🎮 Game Strategy Optimizer",
            "description": "Оптимизирует игровые стратегии для различных жанров игр",
            "short_description": "AI оптимизатор игровых стратегий",
            "category": AgentCategory.GAMING,
            "tags": ["gaming", "strategy", "optimization", "tactics"],
            "base_price": 3 * (10 ** 9),  # 3 NOTPUNKS
            "docker_image": "neuronest/game-strategy",
            "input_schema": {
                "type": "object",
                "properties": {
                    "game_name": {"type": "string", "description": "Название игры"},
                    "game_type": {"type": "string", "enum": ["moba", "fps", "rts", "rpg", "strategy"]},
                    "current_level": {"type": "string", "description": "Текущий уровень игрока"},
                    "goals": {"type": "string", "description": "Игровые цели"}
                },
                "required": ["game_name", "game_type"]
            },
            "required_apis": ["openai"],
            "author": "NeuroNest Team"
        }
    ]
    
    for agent_data in demo_agents:
        agent = Agent(**agent_data)
        db.add(agent)
        logger.info(f"✅ Создан агент: {agent.display_name}")


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