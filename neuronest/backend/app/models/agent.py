"""
Модели AI агентов NeuroNest
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, BigInteger, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, Dict, Any
import enum

from app.core.database import Base
from app.core.constants import from_minimal_units


class AgentCategory(str, enum.Enum):
    """Категории AI агентов"""
    GAMING = "gaming"
    BUSINESS = "business"
    FINANCE = "finance"
    RESEARCH = "research"
    HEALTH = "health"
    PRODUCTIVITY = "productivity"
    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"
    DEVELOPMENT = "development"  # Добавлено для разработки


class AgentStatus(str, enum.Enum):
    """Статусы агентов"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    MAINTENANCE = "maintenance"


class ExecutionStatus(str, enum.Enum):
    """Статусы выполнения агентов"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class Agent(Base):
    """Модель AI агента"""
    
    __tablename__ = "agents"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    short_description = Column(String(500), nullable=True)
    
    # Категория и теги
    category = Column(Enum(AgentCategory), index=True, nullable=False)
    tags = Column(JSON, default=list)  # Список тегов для поиска
    
    # Статус и доступность
    status = Column(Enum(AgentStatus), default=AgentStatus.ACTIVE, index=True)
    is_featured = Column(Boolean, default=False)  # Рекомендуемые агенты
    popularity_score = Column(Integer, default=0)  # Счетчик популярности
    
    # Ценообразование
    base_price = Column(BigInteger, nullable=False)  # Цена в токенах NOTPUNKS
    dynamic_pricing = Column(Boolean, default=False)  # Динамическое ценообразование
    
    # Технические характеристики
    docker_image = Column(String(200), nullable=False)
    docker_tag = Column(String(50), default="latest")
    execution_timeout = Column(Integer, default=300)  # Таймаут в секундах
    memory_limit = Column(String(20), default="512m")
    cpu_limit = Column(String(20), default="0.5")
    
    # Конфигурация
    input_schema = Column(JSON, nullable=False)  # JSON Schema для входных параметров
    output_schema = Column(JSON, nullable=True)  # JSON Schema для выходных данных
    required_apis = Column(JSON, default=list)  # Список требуемых API ключей
    environment_vars = Column(JSON, default=dict)  # Переменные окружения
    
    # Метаданные
    author = Column(String(100), nullable=True)
    version = Column(String(20), default="1.0.0")
    readme = Column(Text, nullable=True)  # Подробное описание
    avatar_url = Column(String(500), nullable=True)  # URL изображения агента
    
    # Статистика
    total_executions = Column(Integer, default=0)
    successful_executions = Column(Integer, default=0)
    avg_execution_time = Column(Integer, default=0)  # Среднее время выполнения в секундах
    rating = Column(Integer, default=0)  # Рейтинг от 0 до 100
    
    # Временные метки
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_execution_at = Column(DateTime, nullable=True)
    
    # Связи
    executions = relationship("AgentExecution", back_populates="agent")
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name={self.name}, category={self.category})>"
    
    @property
    def price_formatted(self) -> float:
        """Цена в удобном для чтения формате"""
        return self.base_price / (10 ** 9)
    
    @property
    def success_rate(self) -> float:
        """Процент успешных выполнений"""
        if self.total_executions == 0:
            return 0.0
        return (self.successful_executions / self.total_executions) * 100
    
    @property
    def avg_execution_time_formatted(self) -> str:
        """Среднее время выполнения в удобном формате"""
        if self.avg_execution_time < 60:
            return f"{self.avg_execution_time}с"
        elif self.avg_execution_time < 3600:
            minutes = self.avg_execution_time // 60
            seconds = self.avg_execution_time % 60
            return f"{minutes}м {seconds}с"
        else:
            hours = self.avg_execution_time // 3600
            minutes = (self.avg_execution_time % 3600) // 60
            return f"{hours}ч {minutes}м"
    
    def update_statistics(self, execution_time: int, was_successful: bool) -> None:
        """Обновление статистики агента"""
        self.total_executions += 1
        
        if was_successful:
            self.successful_executions += 1
        
        # Обновляем среднее время выполнения
        if self.avg_execution_time == 0:
            self.avg_execution_time = execution_time
        else:
            self.avg_execution_time = (
                (self.avg_execution_time * (self.total_executions - 1) + execution_time) 
                // self.total_executions
            )
        
        self.last_execution_at = datetime.utcnow()
        
        # Обновляем рейтинг на основе успешности
        success_weight = 0.7
        popularity_weight = 0.3
        
        success_score = self.success_rate
        popularity_score = min(100, self.total_executions)
        
        self.rating = int(success_score * success_weight + popularity_score * popularity_weight)
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API"""
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "short_description": self.short_description,
            "category": self.category.value,
            "tags": self.tags,
            "status": self.status.value,
            "is_featured": self.is_featured,
            "base_price": self.price_formatted,
            "required_apis": self.required_apis,
            "author": self.author,
            "version": self.version,
            "avatar_url": self.avatar_url,
            "total_executions": self.total_executions,
            "success_rate": self.success_rate,
            "avg_execution_time": self.avg_execution_time_formatted,
            "rating": self.rating,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_execution_at": self.last_execution_at.isoformat() if self.last_execution_at else None
        }


class AgentExecution(Base):
    """Модель выполнения агента"""
    
    __tablename__ = "agent_executions"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String(100), unique=True, index=True, nullable=False)  # UUID
    
    # Связи
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), index=True, nullable=False)
    
    # Статус выполнения
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING, index=True)
    progress = Column(Integer, default=0)  # Прогресс выполнения 0-100%
    
    # Входные и выходные данные
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    logs = Column(Text, nullable=True)
    
    # Технические данные
    docker_container_id = Column(String(100), nullable=True)
    execution_time = Column(Integer, nullable=True)  # Время выполнения в секундах
    
    # Финансовые данные
    price_paid = Column(BigInteger, nullable=False)
    commission_paid = Column(BigInteger, nullable=False)
    
    # Временные метки
    created_at = Column(DateTime, default=func.now())
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Связи
    user = relationship("User", back_populates="executions")
    agent = relationship("Agent", back_populates="executions")
    
    def __repr__(self):
        return f"<AgentExecution(id={self.id}, execution_id={self.execution_id}, status={self.status})>"
    
    @property
    def duration(self) -> Optional[int]:
        """Длительность выполнения в секундах"""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds())
        return None
    
    @property
    def is_running(self) -> bool:
        """Проверка, выполняется ли агент"""
        return self.status in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING]
    
    @property
    def is_completed(self) -> bool:
        """Проверка, завершено ли выполнение"""
        return self.status in [
            ExecutionStatus.COMPLETED, 
            ExecutionStatus.FAILED, 
            ExecutionStatus.CANCELLED, 
            ExecutionStatus.TIMEOUT
        ]
    
    @property
    def was_successful(self) -> bool:
        """Проверка, было ли выполнение успешным"""
        return self.status == ExecutionStatus.COMPLETED
    
    def start(self, container_id: str) -> None:
        """Начало выполнения"""
        self.status = ExecutionStatus.RUNNING
        self.started_at = datetime.utcnow()
        self.docker_container_id = container_id
    
    def complete(self, output_data: Dict[str, Any], logs: str = "") -> None:
        """Успешное завершение выполнения"""
        self.status = ExecutionStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.output_data = output_data
        self.logs = logs
        self.execution_time = self.duration
        self.progress = 100
    
    def fail(self, error_message: str, logs: str = "") -> None:
        """Неуспешное завершение выполнения"""
        self.status = ExecutionStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
        self.logs = logs
        self.execution_time = self.duration
    
    def cancel(self) -> None:
        """Отмена выполнения"""
        self.status = ExecutionStatus.CANCELLED
        self.completed_at = datetime.utcnow()
        self.execution_time = self.duration
    
    def timeout(self) -> None:
        """Таймаут выполнения"""
        self.status = ExecutionStatus.TIMEOUT
        self.completed_at = datetime.utcnow()
        self.error_message = "Execution timeout"
        self.execution_time = self.duration
    
    def update_progress(self, progress: int) -> None:
        """Обновление прогресса выполнения"""
        self.progress = max(0, min(100, progress))
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API"""
        return {
            "id": self.id,
            "execution_id": self.execution_id,
            "status": self.status.value,
            "progress": self.progress,
            "agent": self.agent.to_dict() if self.agent else None,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "price_paid": self.price_paid / (10 ** 9),
            "commission_paid": self.commission_paid / (10 ** 9),
            "execution_time": self.execution_time,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        } 