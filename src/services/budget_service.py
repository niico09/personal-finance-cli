"""Servicio de gestión de presupuestos."""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, extract

from src.database.connection import create_db_session
from src.database.models import Budget, BudgetCategory, Transaction, Category, TransactionType
from src.utils.logging import get_logger

logger = get_logger(__name__)


class BudgetService:
    """Servicio para gestión de presupuestos."""

    def __init__(self, db_session: Optional[Session] = None):
        """Inicializar servicio de presupuestos."""
        self._db_session = db_session
    @property
    def db_session(self) -> Session:
        """Obtener sesión de base de datos."""
        if self._db_session is None:
            self._db_session = create_db_session()
        return self._db_session

    def create_budget(
        self,
        name: str,
        period_type: str,
        year: int,
        month: Optional[int] = None,
        description: Optional[str] = None
    ) -> Budget:
        """Crear nuevo presupuesto."""
        try:
            budget = Budget(
                id=str(uuid4()),
                name=name,
                period_type=period_type,
                year=year,
                month=month,
                description=description,
                is_active=True,
                created_at=datetime.now()
            )

            self.db_session.add(budget)
            self.db_session.commit()

            logger.info(f"Presupuesto creado: {budget.id} - {name}")
            return budget

        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error al crear presupuesto: {e}")
            raise

    def add_budget_category(
        self,
        budget_id: str,
        category_name: str,
        allocated_amount: Decimal,
        description: Optional[str] = None
    ) -> BudgetCategory:
        """Agregar categoría a presupuesto."""
        try:
            # Obtener o crear categoría
            category = self._get_or_create_category(category_name)

            budget_category = BudgetCategory(
                id=str(uuid4()),
                budget_id=budget_id,
                category_id=category.id,
                allocated_amount=allocated_amount,
                description=description,
                created_at=datetime.now()
            )

            self.db_session.add(budget_category)
            self.db_session.commit()

            logger.info(f"Categoría agregada al presupuesto: {category_name} - {allocated_amount}")
            return budget_category

        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error al agregar categoría al presupuesto: {e}")
            raise

    def get_budgets(self, active_only: bool = True) -> List[Budget]:
        """Obtener presupuestos."""
        try:
            query = self.db_session.query(Budget)

            if active_only:
                query = query.filter(Budget.is_active == True)

            return query.order_by(Budget.year.desc(), Budget.month.desc()).all()

        except Exception as e:
            logger.error(f"Error al obtener presupuestos: {e}")
            raise

    def get_budget_by_id(self, budget_id: str) -> Optional[Budget]:
        """Obtener presupuesto por ID."""
        try:
            return self.db_session.query(Budget).filter(
                Budget.id == budget_id
            ).first()
        except Exception as e:
            logger.error(f"Error al obtener presupuesto {budget_id}: {e}")
            raise

    def get_current_budget(self, year: int, month: Optional[int] = None) -> Optional[Budget]:
        """Obtener presupuesto actual."""
        try:
            query = self.db_session.query(Budget).filter(
                and_(
                    Budget.year == year,
                    Budget.is_active == True
                )
            )

            if month:
                query = query.filter(Budget.month == month)
            else:
                query = query.filter(Budget.month.is_(None))

            return query.first()

        except Exception as e:
            logger.error(f"Error al obtener presupuesto actual: {e}")
            raise

    def get_budget_analysis(self, budget_id: str) -> Dict[str, Any]:
        """Analizar progreso del presupuesto."""
        try:
            budget = self.get_budget_by_id(budget_id)
            if not budget:
                raise ValueError(f"Presupuesto no encontrado: {budget_id}")

            # Obtener categorías del presupuesto
            budget_categories = (
                self.db_session.query(BudgetCategory)
                .filter(BudgetCategory.budget_id == budget_id)
                .all()
            )

            # Calcular fechas del período
            if budget.period_type == "monthly":
                start_date = date(budget.year, budget.month or 1, 1)
                if budget.month == 12:
                    end_date = date(budget.year + 1, 1, 1)
                else:
                    end_date = date(budget.year, (budget.month or 1) + 1, 1)
            else:  # yearly
                start_date = date(budget.year, 1, 1)
                end_date = date(budget.year + 1, 1, 1)

            # Analizar cada categoría
            category_analysis = []
            total_allocated = Decimal('0')
            total_spent = Decimal('0')

            for budget_cat in budget_categories:
                # Obtener gastos reales de la categoría
                spent_amount = (
                    self.db_session.query(func.sum(Transaction.amount))
                    .filter(
                        and_(
                            Transaction.category_id == budget_cat.category_id,
                            Transaction.transaction_type == TransactionType.EXPENSE,
                            Transaction.transaction_date >= start_date,
                            Transaction.transaction_date < end_date
                        )
                    )
                    .scalar()
                ) or Decimal('0')

                allocated = budget_cat.allocated_amount
                remaining = allocated - spent_amount
                percentage_used = (spent_amount / allocated * 100) if allocated > 0 else 0

                category_analysis.append({
                    'category_name': budget_cat.category.name,
                    'allocated_amount': allocated,
                    'spent_amount': spent_amount,
                    'remaining_amount': remaining,
                    'percentage_used': float(percentage_used),
                    'is_over_budget': spent_amount > allocated
                })

                total_allocated += allocated
                total_spent += spent_amount

            return {
                'budget': {
                    'id': budget.id,
                    'name': budget.name,
                    'period_type': budget.period_type,
                    'year': budget.year,
                    'month': budget.month
                },
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                },
                'totals': {
                    'allocated_amount': total_allocated,
                    'spent_amount': total_spent,
                    'remaining_amount': total_allocated - total_spent,
                    'percentage_used': float((total_spent / total_allocated * 100) if total_allocated > 0 else 0)
                },
                'categories': category_analysis,
                'is_over_budget': total_spent > total_allocated
            }

        except Exception as e:
            logger.error(f"Error al analizar presupuesto {budget_id}: {e}")
            raise

    def update_budget(self, budget_id: str, **kwargs) -> Optional[Budget]:
        """Actualizar presupuesto."""
        try:
            budget = self.get_budget_by_id(budget_id)
            if not budget:
                return None

            allowed_fields = ['name', 'description', 'is_active']

            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    setattr(budget, field, value)

            budget.updated_at = datetime.now()
            self.db_session.commit()

            logger.info(f"Presupuesto actualizado: {budget_id}")
            return budget

        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error al actualizar presupuesto {budget_id}: {e}")
            raise

    def delete_budget(self, budget_id: str) -> bool:
        """Eliminar presupuesto."""
        try:
            budget = self.get_budget_by_id(budget_id)
            if not budget:
                return False

            # Eliminar categorías del presupuesto primero
            self.db_session.query(BudgetCategory).filter(
                BudgetCategory.budget_id == budget_id
            ).delete()

            # Eliminar presupuesto
            self.db_session.delete(budget)
            self.db_session.commit()

            logger.info(f"Presupuesto eliminado: {budget_id}")
            return True

        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error al eliminar presupuesto {budget_id}: {e}")
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

    def close(self):
        """Cerrar sesión de base de datos."""
        if self._db_session:
            self._db_session.close()
