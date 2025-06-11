"""
Модель транзакций NeuroNest
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, BigInteger, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import enum

from app.core.database import Base
from app.core.constants import from_minimal_units


class TransactionType(str, enum.Enum):
    """Типы транзакций"""
    PAYMENT = "payment"  # Оплата агента
    REFUND = "refund"   # Возврат средств
    DEPOSIT = "deposit"  # Пополнение баланса
    WITHDRAWAL = "withdrawal"  # Вывод средств
    COMMISSION = "commission"  # Комиссия платформы


class TransactionStatus(str, enum.Enum):
    """Статусы транзакций"""
    PENDING = "pending"  # Ожидает подтверждения
    CONFIRMING = "confirming"  # Подтверждается в блокчейне
    COMPLETED = "completed"  # Завершена
    FAILED = "failed"  # Неудачная
    CANCELLED = "cancelled"  # Отменена
    EXPIRED = "expired"  # Истекла


class Transaction(Base):
    """Модель транзакции"""
    
    __tablename__ = "transactions"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(100), unique=True, index=True, nullable=False)  # UUID
    
    # Связи
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    execution_id = Column(Integer, ForeignKey("agent_executions.id"), index=True, nullable=True)
    
    # Тип и статус
    type = Column(Enum(TransactionType), index=True, nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, index=True)
    
    # Суммы (в минимальных единицах NOTPUNKS токена)
    amount = Column(BigInteger, nullable=False)  # Основная сумма
    commission = Column(BigInteger, default=0)  # Комиссия платформы
    total_amount = Column(BigInteger, nullable=False)  # Общая сумма
    
    # Blockchain данные
    ton_transaction_hash = Column(String(100), index=True, nullable=True)
    ton_block_height = Column(BigInteger, nullable=True)
    confirmations = Column(Integer, default=0)
    
    # Адреса кошельков
    from_address = Column(String(100), nullable=True)
    to_address = Column(String(100), nullable=True)
    
    # Дополнительные данные
    description = Column(Text, nullable=True)
    metadata = Column(JSON, default=dict)  # Дополнительные данные в JSON
    
    # Временные метки
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    confirmed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Связи
    user = relationship("User", back_populates="transactions")
    execution = relationship("AgentExecution", backref="transaction")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, transaction_id={self.transaction_id}, type={self.type}, status={self.status})>"
    
    @property
    def amount_formatted(self) -> float:
        """Сумма в удобном для чтения формате"""
        return from_minimal_units(self.amount)
    
    @property
    def commission_formatted(self) -> float:
        """Комиссия в удобном для чтения формате"""
        return from_minimal_units(self.commission)
    
    @property
    def total_amount_formatted(self) -> float:
        """Общая сумма в удобном для чтения формате"""
        return from_minimal_units(self.total_amount)
    
    @property
    def is_pending(self) -> bool:
        """Проверка, ожидает ли транзакция подтверждения"""
        return self.status in [TransactionStatus.PENDING, TransactionStatus.CONFIRMING]
    
    @property
    def is_completed(self) -> bool:
        """Проверка, завершена ли транзакция"""
        return self.status == TransactionStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Проверка, неудачная ли транзакция"""
        return self.status in [TransactionStatus.FAILED, TransactionStatus.CANCELLED, TransactionStatus.EXPIRED]
    
    @property
    def needs_confirmation(self) -> bool:
        """Проверка, нужно ли подтверждение транзакции"""
        from app.core.config import settings
        return (
            self.status == TransactionStatus.CONFIRMING and
            self.confirmations < settings.PAYMENT_CONFIRMATION_BLOCKS
        )
    
    def set_blockchain_data(self, tx_hash: str, block_height: int, from_addr: str, to_addr: str) -> None:
        """Установка blockchain данных"""
        self.ton_transaction_hash = tx_hash
        self.ton_block_height = block_height
        self.from_address = from_addr
        self.to_address = to_addr
        self.status = TransactionStatus.CONFIRMING
    
    def add_confirmation(self) -> None:
        """Добавление подтверждения"""
        self.confirmations += 1
        
        from app.core.config import settings
        if self.confirmations >= settings.PAYMENT_CONFIRMATION_BLOCKS:
            self.confirm()
    
    def confirm(self) -> None:
        """Подтверждение транзакции"""
        self.status = TransactionStatus.COMPLETED
        self.confirmed_at = datetime.utcnow()
    
    def fail(self, reason: str = "") -> None:
        """Провал транзакции"""
        self.status = TransactionStatus.FAILED
        if reason:
            self.description = reason
    
    def cancel(self) -> None:
        """Отмена транзакции"""
        self.status = TransactionStatus.CANCELLED
    
    def expire(self) -> None:
        """Истечение транзакции"""
        self.status = TransactionStatus.EXPIRED
    
    def is_expired(self) -> bool:
        """Проверка, истекла ли транзакция"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @classmethod
    def create_payment_transaction(
        cls, 
        user_id: int, 
        execution_id: int, 
        amount: int, 
        commission: int,
        transaction_id: str,
        expires_in_minutes: int = 15
    ) -> "Transaction":
        """Создание транзакции оплаты агента"""
        transaction = cls(
            transaction_id=transaction_id,
            user_id=user_id,
            execution_id=execution_id,
            type=TransactionType.PAYMENT,
            amount=amount,
            commission=commission,
            total_amount=amount + commission,
            description=f"Payment for agent execution #{execution_id}",
            expires_at=datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        )
        return transaction
    
    @classmethod
    def create_refund_transaction(
        cls,
        user_id: int,
        execution_id: int,
        amount: int,
        transaction_id: str,
        original_transaction_id: str
    ) -> "Transaction":
        """Создание транзакции возврата"""
        transaction = cls(
            transaction_id=transaction_id,
            user_id=user_id,
            execution_id=execution_id,
            type=TransactionType.REFUND,
            amount=amount,
            commission=0,
            total_amount=amount,
            description=f"Refund for failed execution #{execution_id}",
            metadata={"original_transaction_id": original_transaction_id}
        )
        return transaction
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API"""
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "type": self.type.value,
            "status": self.status.value,
            "amount": self.amount_formatted,
            "commission": self.commission_formatted,
            "total_amount": self.total_amount_formatted,
            "ton_transaction_hash": self.ton_transaction_hash,
            "confirmations": self.confirmations,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "confirmed_at": self.confirmed_at.isoformat() if self.confirmed_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }


# Вспомогательные функции для работы с транзакциями

def calculate_commission(amount: int, commission_rate: float) -> int:
    """Расчет комиссии"""
    return int(amount * commission_rate)


def calculate_total_with_commission(amount: int, commission_rate: float) -> tuple[int, int]:
    """Расчет общей суммы с комиссией"""
    commission = calculate_commission(amount, commission_rate)
    total = amount + commission
    return commission, total 