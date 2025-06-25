"""Servicio de gestión de transacciones."""

from __future__ import annotations

import json
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, extract

from src.database.connection import create_db_session
from src.database.models import Transaction, Category, Account, TransactionType
from src.utils.logging import get_logger

logger = get_logger(__name__)


class TransactionService:
    """Servicio para gestión de transacciones."""

    def __init__(self, db_session: Optional[Session] = None):
        """Inicializar servicio de transacciones."""
        self._db_session = db_session
    @property
    def db_session(self) -> Session:
        """Obtener sesión de base de datos."""
        if self._db_session is None:
            self._db_session = create_db_session()
        return self._db_session

    def create_transaction(
        self,
        amount: Decimal,
        description: str,
        transaction_type: TransactionType,
        category_name: str = "general",
        account_name: str = "default",
        payment_method: str = "cash",
        tags: Optional[List[str]] = None,
        notes: Optional[str] = None,
        transaction_date: Optional[datetime] = None
    ) -> Transaction:
        """Crear nueva transacción."""
        try:
            # Obtener o crear categoría
            category = self._get_or_create_category(category_name)

            # Obtener o crear cuenta
            account = self._get_or_create_account(account_name)
              # Crear transacción
            transaction = Transaction(
                id=str(uuid4()),
                amount=amount,
                description=description,
                transaction_type=transaction_type,
                category_id=category.id,
                account_id=account.id,
                payment_method=payment_method,
                notes=notes,
                transaction_date=transaction_date or datetime.now(),
                created_at=datetime.now()
            )

            # Establecer tags usando JSON
            if tags:
                transaction.tags = json.dumps(tags)

            self.db_session.add(transaction)
            self.db_session.commit()

            logger.info(f"Transacción creada: {transaction.id} - {amount} - {description}")
            return transaction

        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error al crear transacción: {e}")
            raise

    def get_transactions(
        self,
        limit: int = 50,
        offset: int = 0,
        transaction_type: Optional[TransactionType] = None,
        category_name: Optional[str] = None,
        account_name: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        tags: Optional[List[str]] = None,
        search_text: Optional[str] = None,
        order_by: str = "date_desc"
    ) -> List[Transaction]:
        """Obtener transacciones con filtros."""
        try:
            query = self.db_session.query(Transaction)

            # Aplicar filtros
            if transaction_type:
                query = query.filter(Transaction.transaction_type == transaction_type)

            if category_name:
                query = query.join(Category).filter(Category.name == category_name)

            if account_name:
                query = query.join(Account).filter(Account.name == account_name)

            if start_date:
                query = query.filter(Transaction.transaction_date >= start_date)

            if end_date:
                query = query.filter(Transaction.transaction_date <= end_date)

            if min_amount is not None:
                query = query.filter(Transaction.amount >= min_amount)

            if max_amount is not None:
                query = query.filter(Transaction.amount <= max_amount)

            if tags:
                for tag in tags:
                    query = query.filter(Transaction.tags.contains([tag]))

            if search_text:
                search_pattern = f"%{search_text}%"
                query = query.filter(
                    or_(
                        Transaction.description.ilike(search_pattern),
                        Transaction.notes.ilike(search_pattern)
                    )
                )

            # Aplicar ordenamiento
            if order_by == "date_desc":
                query = query.order_by(desc(Transaction.transaction_date))
            elif order_by == "date_asc":
                query = query.order_by(asc(Transaction.transaction_date))
            elif order_by == "amount_desc":
                query = query.order_by(desc(Transaction.amount))
            elif order_by == "amount_asc":
                query = query.order_by(asc(Transaction.amount))

            # Aplicar paginación
            query = query.offset(offset).limit(limit)

            return query.all()

        except Exception as e:
            logger.error(f"Error al obtener transacciones: {e}")
            raise

    def get_transaction_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """Obtener transacción por ID."""
        try:
            return self.db_session.query(Transaction).filter(
                Transaction.id == transaction_id
            ).first()
        except Exception as e:
            logger.error(f"Error al obtener transacción {transaction_id}: {e}")
            raise

    def update_transaction(
        self,
        transaction_id: str,
        **kwargs
    ) -> Optional[Transaction]:
        """Actualizar transacción."""
        try:
            transaction = self.get_transaction_by_id(transaction_id)
            if not transaction:
                return None

            # Actualizar campos permitidos
            allowed_fields = [
                'amount', 'description', 'transaction_type', 'payment_method',
                'tags', 'notes', 'transaction_date'
            ]

            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    setattr(transaction, field, value)

            # Actualizar categoría si se proporciona
            if 'category_name' in kwargs:
                category = self._get_or_create_category(kwargs['category_name'])
                transaction.category_id = category.id

            # Actualizar cuenta si se proporciona
            if 'account_name' in kwargs:
                account = self._get_or_create_account(kwargs['account_name'])
                transaction.account_id = account.id

            transaction.updated_at = datetime.now()
            self.db_session.commit()

            logger.info(f"Transacción actualizada: {transaction_id}")
            return transaction

        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error al actualizar transacción {transaction_id}: {e}")
            raise

    def delete_transaction(self, transaction_id: str) -> bool:
        """Eliminar transacción."""
        try:
            transaction = self.get_transaction_by_id(transaction_id)
            if not transaction:
                return False

            self.db_session.delete(transaction)
            self.db_session.commit()

            logger.info(f"Transacción eliminada: {transaction_id}")
            return True

        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error al eliminar transacción {transaction_id}: {e}")
            raise

    def get_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        account_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Obtener resumen de transacciones."""
        try:
            query = self.db_session.query(Transaction)

            # Aplicar filtros de fecha
            if start_date:
                query = query.filter(Transaction.transaction_date >= start_date)
            if end_date:
                query = query.filter(Transaction.transaction_date <= end_date)

            # Filtrar por cuenta si se especifica
            if account_name:
                query = query.join(Account).filter(Account.name == account_name)

            # Calcular totales por tipo
            income_total = query.filter(
                Transaction.transaction_type == TransactionType.INCOME
            ).with_entities(func.sum(Transaction.amount)).scalar() or Decimal('0')

            expense_total = query.filter(
                Transaction.transaction_type == TransactionType.EXPENSE
            ).with_entities(func.sum(Transaction.amount)).scalar() or Decimal('0')

            # Obtener top categorías de gastos
            top_categories = (
                query.filter(Transaction.transaction_type == TransactionType.EXPENSE)
                .join(Category)
                .with_entities(
                    Category.name,
                    func.sum(Transaction.amount).label('total')
                )
                .group_by(Category.name)
                .order_by(desc('total'))
                .limit(5)
                .all()
            )

            # Contar transacciones
            total_transactions = query.count()

            return {
                'income_total': income_total,
                'expense_total': expense_total,
                'balance': income_total - expense_total,
                'total_transactions': total_transactions,
                'top_categories': [
                    {'name': cat[0], 'amount': cat[1]}
                    for cat in top_categories
                ],
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                }
            }

        except Exception as e:
            logger.error(f"Error al obtener resumen: {e}")
            raise

    def _get_or_create_category(self, name: str) -> Category:
        """Obtener o crear categoría."""
        category = self.db_session.query(Category).filter(
            Category.name == name
        ).first()

        if not category:
            category = Category(
                id=str(uuid4()),
                name=name,
                description=f"Categoría {name}",
                created_at=datetime.now()
            )
            self.db_session.add(category)
            self.db_session.flush()

        return category

    def _get_or_create_account(self, name: str) -> Account:
        """Obtener o crear cuenta."""
        account = self.db_session.query(Account).filter(
            Account.name == name
        ).first()

        if not account:
            account = Account(
                id=str(uuid4()),
                name=name,
                account_type="general",
                balance=Decimal('0'),
                created_at=datetime.now()
            )
            self.db_session.add(account)
            self.db_session.flush()

        return account

    def close(self):
        """Cerrar sesión de base de datos."""
        if self._db_session:
            self._db_session.close()
