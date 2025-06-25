"""Modelos de base de datos para Sales Command."""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

# Base para todos los modelos
Base = declarative_base()


class TransactionType(str, Enum):
    """Tipos de transacción."""
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class InvestmentType(str, Enum):
    """Tipos de inversión."""
    STOCK = "stock"
    BOND = "bond"
    FUND = "fund"
    CRYPTO = "crypto"
    REAL_ESTATE = "real_estate"
    OTHER = "other"


class PaymentMethod(str, Enum):
    """Métodos de pago."""
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    OTHER = "other"


class RecurrenceFrequency(str, Enum):
    """Frecuencias de recurrencia."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class Category(Base):
    """Modelo para categorías de transacciones."""

    __tablename__ = "categories"

    id = Column(String(36), primary_key=True, index=True)  # UUID
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    color = Column(String(7), default="#6B7280")  # Color hex
    icon = Column(String(50), default="💰")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)    # Relaciones
    transactions = relationship("Transaction", back_populates="category")

    def __repr__(self) -> str:
        return f"<Category(name='{self.name}')>"


class Account(Base):
    """Modelo para cuentas bancarias y tarjetas."""

    __tablename__ = "accounts"

    id = Column(String(36), primary_key=True, index=True)  # UUID
    name = Column(String(100), nullable=False)
    account_type = Column(String(50), nullable=False)  # bank, credit_card, cash
    balance = Column(Numeric(10, 2), default=0.00)
    credit_limit = Column(Numeric(10, 2))  # Para tarjetas de crédito
    closing_day = Column(Integer)  # Día de cierre (1-31)
    due_day = Column(Integer)  # Día de vencimiento (1-31)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    transactions = relationship("Transaction", back_populates="account")

    def __repr__(self) -> str:
        return f"<Account(name='{self.name}', type='{self.account_type}')>"


class Transaction(Base):
    """Modelo para transacciones financieras."""

    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, index=True)  # UUID
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String(500), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # income, expense, transfer
    payment_method = Column(String(50), default=PaymentMethod.CASH)
    transaction_date = Column(DateTime, nullable=False, index=True)

    # Claves foráneas
    category_id = Column(String(36), ForeignKey("categories.id"))
    account_id = Column(String(36), ForeignKey("accounts.id"))

    # Campos adicionales
    tags = Column(Text)  # JSON array as string
    location = Column(String(200))
    notes = Column(Text)
    is_recurring = Column(Boolean, default=False)
    recurring_id = Column(Integer, ForeignKey("recurring_transactions.id"))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    category = relationship("Category", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    recurring_transaction = relationship("RecurringTransaction", back_populates="transactions")

    @hybrid_property
    def parsed_tags(self) -> Optional[List[str]]:
        """Devuelve los tags como una lista, o None si no hay tags."""
        if self.tags:
            return json.loads(self.tags)
        return None

    @parsed_tags.expression
    def parsed_tags(cls):
        """Permite filtrar por tags en consultas."""
        return cls.tags

    def __repr__(self) -> str:
        return f"<Transaction(amount={self.amount}, type='{self.transaction_type}')>"


class RecurringTransaction(Base):
    """Modelo para transacciones recurrentes."""

    __tablename__ = "recurring_transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String(500), nullable=False)
    transaction_type = Column(String(20), nullable=False)
    frequency = Column(String(20), nullable=False)  # daily, weekly, monthly, etc.

    # Fechas
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)  # Opcional
    next_execution = Column(DateTime, nullable=False)
    last_execution = Column(DateTime)    # Claves foráneas
    category_id = Column(String(36), ForeignKey("categories.id"))
    account_id = Column(String(36), ForeignKey("accounts.id"))

    # Configuración
    is_active = Column(Boolean, default=True)
    auto_execute = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    transactions = relationship("Transaction", back_populates="recurring_transaction")

    def __repr__(self) -> str:
        return f"<RecurringTransaction(amount={self.amount}, frequency='{self.frequency}')>"


class Budget(Base):
    """Modelo para presupuestos."""

    __tablename__ = "budgets"

    id = Column(String(36), primary_key=True, index=True)  # UUID
    name = Column(String(100), nullable=False)
    period_type = Column(String(20), nullable=False)  # monthly, yearly
    year = Column(Integer, nullable=False)
    month = Column(Integer)  # Para presupuestos mensuales
    description = Column(Text)

    # Configuración
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    budget_categories = relationship("BudgetCategory", back_populates="budget", cascade="all, delete-orphan")    # Constraint único por período
    __table_args__ = (
        UniqueConstraint('period_type', 'year', 'month', name='uq_budget_period'),
    )

    def __repr__(self) -> str:
        return f"<Budget(name='{self.name}', period='{self.period_type}')>"


class BudgetCategory(Base):
    """Modelo para categorías de presupuesto."""

    __tablename__ = "budget_categories"

    id = Column(String(36), primary_key=True, index=True)  # UUID
    budget_id = Column(String(36), ForeignKey("budgets.id"), nullable=False)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=False)
    allocated_amount = Column(Numeric(10, 2), nullable=False)
    description = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    budget = relationship("Budget", back_populates="budget_categories")
    category = relationship("Category")

    # Constraint único por presupuesto y categoría
    __table_args__ = (
        UniqueConstraint('budget_id', 'category_id', name='uq_budget_category'),
    )

    def __repr__(self) -> str:
        return f"<BudgetCategory(budget_id='{self.budget_id}', category_id='{self.category_id}', amount={self.allocated_amount})>"


class Investment(Base):
    """Modelo para inversiones."""

    __tablename__ = "investments"

    id = Column(String(36), primary_key=True, index=True)  # UUID
    name = Column(String(200), nullable=False)
    investment_type = Column(String(50), nullable=False)  # Enum as string
    initial_amount = Column(Numeric(15, 2), nullable=False)
    current_value = Column(Numeric(15, 2), nullable=False)
    shares = Column(Numeric(15, 6))  # Opcional
    purchase_price = Column(Numeric(10, 2))  # Opcional
    purchase_date = Column(DateTime, nullable=False)
    description = Column(Text)
    last_updated = Column(DateTime)

    # Estado
    is_active = Column(Boolean, default=True)    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    dividends = relationship("Dividend", back_populates="investment")

    def __repr__(self) -> str:
        return f"<Investment(name='{self.name}', type='{self.investment_type}', value={self.current_value})>"


class Dividend(Base):
    """Modelo para dividendos e intereses."""

    __tablename__ = "dividends"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(DateTime, nullable=False)    # Claves foráneas
    investment_id = Column(String(36), ForeignKey("investments.id"))

    # Campos adicionales
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    investment = relationship("Investment", back_populates="dividends")

    def __repr__(self) -> str:
        return f"<Dividend(amount={self.amount}, date={self.payment_date})>"


class Goal(Base):
    """Modelo para metas financieras."""

    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    target_amount = Column(Numeric(10, 2), nullable=False)
    current_amount = Column(Numeric(10, 2), default=0.00)
    target_date = Column(DateTime)

    # Configuración
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)  # 1=alta, 2=media, 3=baja

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Goal(name='{self.name}', target={self.target_amount})>"
