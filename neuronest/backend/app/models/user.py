"""
Модель пользователя NeuroNest
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, BigInteger, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.core.database import Base


class User(Base):
    """Модель пользователя"""
    
    __tablename__ = "users"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String(100), index=True, nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    language_code = Column(String(10), default="ru")
    
    # Статус и права доступа
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    has_nft_access = Column(Boolean, default=False)
    nft_collections = Column(JSON, default=list)  # Список NFT коллекций пользователя
    
    # TON кошелек
    ton_wallet_address = Column(String(100), index=True, nullable=True)
    ton_wallet_connected_at = Column(DateTime, nullable=True)
    
    # Балансы и статистика
    notpunks_balance = Column(BigInteger, default=0)  # Баланс в токенах NOTPUNKS
    total_spent = Column(BigInteger, default=0)  # Общая сумма потраченных токенов
    agents_used_count = Column(Integer, default=0)  # Количество использованных агентов
    
    # Дополнительные данные
    settings = Column(JSON, default=dict)  # Пользовательские настройки
    api_keys = Column(Text, nullable=True)  # Зашифрованные API ключи пользователя
    
    # Временные метки
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_activity_at = Column(DateTime, default=func.now())
    
    # Связи с другими таблицами
    executions = relationship("AgentExecution", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"
    
    @property
    def display_name(self) -> str:
        """Отображаемое имя пользователя"""
        if self.username:
            return f"@{self.username}"
        elif self.first_name:
            return self.first_name
        else:
            return f"User {self.telegram_id}"
    
    @property
    def full_name(self) -> str:
        """Полное имя пользователя"""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) if parts else self.display_name
    
    @property
    def notpunks_balance_formatted(self) -> float:
        """Баланс NOTPUNKS в удобном для чтения формате"""
        return self.notpunks_balance / (10 ** 9)  # 9 decimal places
    
    def has_nft_from_collections(self, collections: List[str]) -> bool:
        """Проверка наличия NFT из указанных коллекций"""
        if not self.nft_collections:
            return False
        
        user_collections = set(self.nft_collections)
        target_collections = set(collections)
        
        return bool(user_collections.intersection(target_collections))
    
    def add_nft_collection(self, collection_address: str) -> None:
        """Добавление NFT коллекции к пользователю"""
        if not self.nft_collections:
            self.nft_collections = []
        
        if collection_address not in self.nft_collections:
            self.nft_collections.append(collection_address)
            
        # Обновляем статус доступа
        from app.core.config import settings
        self.has_nft_access = self.has_nft_from_collections(settings.nft_collections)
    
    def remove_nft_collection(self, collection_address: str) -> None:
        """Удаление NFT коллекции у пользователя"""
        if self.nft_collections and collection_address in self.nft_collections:
            self.nft_collections.remove(collection_address)
            
        # Обновляем статус доступа
        from app.core.config import settings
        self.has_nft_access = self.has_nft_from_collections(settings.nft_collections)
    
    def update_activity(self) -> None:
        """Обновление времени последней активности"""
        self.last_activity_at = datetime.utcnow()
    
    def can_execute_agent(self, agent_price: int) -> bool:
        """Проверка возможности запуска агента"""
        return (
            self.is_active and 
            self.has_nft_access and 
            self.notpunks_balance >= agent_price
        )
    
    def get_commission_rate(self) -> float:
        """Получение размера комиссии для пользователя"""
        from app.core.config import settings
        
        if self.is_premium:
            return settings.PREMIUM_COMMISSION_RATE
        else:
            return settings.COMMISSION_RATE
    
    def debit_balance(self, amount: int) -> bool:
        """Списание средств с баланса"""
        if self.notpunks_balance >= amount:
            self.notpunks_balance -= amount
            self.total_spent += amount
            return True
        return False
    
    def credit_balance(self, amount: int) -> None:
        """Зачисление средств на баланс"""
        self.notpunks_balance += amount
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API"""
        return {
            "id": self.id,
            "telegram_id": self.telegram_id,
            "username": self.username,
            "display_name": self.display_name,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_premium": self.is_premium,
            "has_nft_access": self.has_nft_access,
            "nft_collections": self.nft_collections,
            "ton_wallet_address": self.ton_wallet_address,
            "notpunks_balance": self.notpunks_balance_formatted,
            "total_spent": self.total_spent / (10 ** 9),
            "agents_used_count": self.agents_used_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_activity_at": self.last_activity_at.isoformat() if self.last_activity_at else None
        } 