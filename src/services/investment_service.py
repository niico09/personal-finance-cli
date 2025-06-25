"""Servicio de gestión de inversiones."""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from src.database.connection import create_db_session
from src.database.models import Investment, InvestmentType
from src.utils.logging import get_logger

logger = get_logger(__name__)


class InvestmentService:
    """Servicio para gestión de inversiones."""

    def __init__(self, db_session: Optional[Session] = None):
        """Inicializar servicio de inversiones."""
        self._db_session = db_session
    @property
    def db_session(self) -> Session:
        """Obtener sesión de base de datos."""
        if self._db_session is None:
            self._db_session = create_db_session()
        return self._db_session

    def create_investment(
        self,
        name: str,
        investment_type: InvestmentType,
        initial_amount: Decimal,
        current_value: Optional[Decimal] = None,
        shares: Optional[Decimal] = None,
        purchase_price: Optional[Decimal] = None,
        description: Optional[str] = None,
        purchase_date: Optional[datetime] = None
    ) -> Investment:
        """Crear nueva inversión."""
        try:
            investment = Investment(
                id=str(uuid4()),
                name=name,
                investment_type=investment_type,
                initial_amount=initial_amount,
                current_value=current_value or initial_amount,
                shares=shares,
                purchase_price=purchase_price,
                description=description,
                purchase_date=purchase_date or datetime.now(),
                is_active=True,
                created_at=datetime.now()
            )

            self.db_session.add(investment)
            self.db_session.commit()

            logger.info(f"Inversión creada: {investment.id} - {name}")
            return investment

        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error al crear inversión: {e}")
            raise

    def get_investments(
        self,
        active_only: bool = True,
        investment_type: Optional[InvestmentType] = None
    ) -> List[Investment]:
        """Obtener inversiones."""
        try:
            query = self.db_session.query(Investment)

            if active_only:
                query = query.filter(Investment.is_active == True)

            if investment_type:
                query = query.filter(Investment.investment_type == investment_type)

            return query.order_by(desc(Investment.purchase_date)).all()

        except Exception as e:
            logger.error(f"Error al obtener inversiones: {e}")
            raise

    def get_investment_by_id(self, investment_id: str) -> Optional[Investment]:
        """Obtener inversión por ID."""
        try:
            return self.db_session.query(Investment).filter(
                Investment.id == investment_id
            ).first()
        except Exception as e:
            logger.error(f"Error al obtener inversión {investment_id}: {e}")
            raise

    def update_investment_value(
        self,
        investment_id: str,
        current_value: Decimal,
        update_date: Optional[datetime] = None
    ) -> Optional[Investment]:
        """Actualizar valor actual de inversión."""
        try:
            investment = self.get_investment_by_id(investment_id)
            if not investment:
                return None

            investment.current_value = current_value
            investment.last_updated = update_date or datetime.now()
            investment.updated_at = datetime.now()

            self.db_session.commit()

            logger.info(f"Valor de inversión actualizado: {investment_id} - {current_value}")
            return investment

        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error al actualizar valor de inversión {investment_id}: {e}")
            raise

    def update_investment(self, investment_id: str, **kwargs) -> Optional[Investment]:
        """Actualizar inversión."""
        try:
            investment = self.get_investment_by_id(investment_id)
            if not investment:
                return None

            allowed_fields = [
                'name', 'current_value', 'shares', 'purchase_price',
                'description', 'is_active'
            ]

            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    setattr(investment, field, value)

            investment.updated_at = datetime.now()
            self.db_session.commit()

            logger.info(f"Inversión actualizada: {investment_id}")
            return investment

        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error al actualizar inversión {investment_id}: {e}")
            raise

    def delete_investment(self, investment_id: str) -> bool:
        """Eliminar inversión."""
        try:
            investment = self.get_investment_by_id(investment_id)
            if not investment:
                return False

            self.db_session.delete(investment)
            self.db_session.commit()

            logger.info(f"Inversión eliminada: {investment_id}")
            return True

        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error al eliminar inversión {investment_id}: {e}")
            raise

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Obtener resumen del portafolio de inversiones."""
        try:
            investments = self.get_investments(active_only=True)

            if not investments:
                return {
                    'total_invested': Decimal('0'),
                    'current_value': Decimal('0'),
                    'total_return': Decimal('0'),
                    'return_percentage': 0.0,
                    'investments_count': 0,
                    'by_type': {},
                    'top_performers': [],
                    'worst_performers': []
                }

            total_invested = sum(inv.initial_amount for inv in investments)
            current_value = sum(inv.current_value for inv in investments)
            total_return = current_value - total_invested
            return_percentage = (total_return / total_invested * 100) if total_invested > 0 else 0

            # Agrupar por tipo
            by_type = {}
            for inv in investments:
                inv_type = inv.investment_type.value
                if inv_type not in by_type:
                    by_type[inv_type] = {
                        'count': 0,
                        'invested': Decimal('0'),
                        'current_value': Decimal('0'),
                        'return': Decimal('0')
                    }

                by_type[inv_type]['count'] += 1
                by_type[inv_type]['invested'] += inv.initial_amount
                by_type[inv_type]['current_value'] += inv.current_value
                by_type[inv_type]['return'] += (inv.current_value - inv.initial_amount)

            # Calcular rendimiento por inversión
            investments_with_return = []
            for inv in investments:
                return_amount = inv.current_value - inv.initial_amount
                return_pct = (return_amount / inv.initial_amount * 100) if inv.initial_amount > 0 else 0

                investments_with_return.append({
                    'id': inv.id,
                    'name': inv.name,
                    'type': inv.investment_type.value,
                    'invested': inv.initial_amount,
                    'current_value': inv.current_value,
                    'return_amount': return_amount,
                    'return_percentage': float(return_pct)
                })

            # Ordenar por rendimiento
            investments_with_return.sort(key=lambda x: x['return_percentage'], reverse=True)

            return {
                'total_invested': total_invested,
                'current_value': current_value,
                'total_return': total_return,
                'return_percentage': float(return_percentage),
                'investments_count': len(investments),
                'by_type': by_type,
                'top_performers': investments_with_return[:5],
                'worst_performers': investments_with_return[-5:] if len(investments_with_return) > 5 else []
            }

        except Exception as e:
            logger.error(f"Error al obtener resumen del portafolio: {e}")
            raise

    def get_investment_performance(
        self,
        investment_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Obtener rendimiento detallado de una inversión."""
        try:
            investment = self.get_investment_by_id(investment_id)
            if not investment:
                raise ValueError(f"Inversión no encontrada: {investment_id}")

            # Calcular métricas básicas
            total_return = investment.current_value - investment.initial_amount
            return_percentage = (total_return / investment.initial_amount * 100) if investment.initial_amount > 0 else 0

            # Calcular días de tenencia
            holding_days = (datetime.now().date() - investment.purchase_date.date()).days

            # Rendimiento anualizado (aproximado)
            if holding_days > 0:
                annualized_return = ((investment.current_value / investment.initial_amount) ** (365.25 / holding_days) - 1) * 100
            else:
                annualized_return = 0

            return {
                'investment': {
                    'id': investment.id,
                    'name': investment.name,
                    'type': investment.investment_type.value,
                    'purchase_date': investment.purchase_date.date()
                },
                'values': {
                    'initial_amount': investment.initial_amount,
                    'current_value': investment.current_value,
                    'shares': investment.shares,
                    'purchase_price': investment.purchase_price
                },
                'performance': {
                    'total_return': total_return,
                    'return_percentage': float(return_percentage),
                    'annualized_return': float(annualized_return) if holding_days > 0 else 0,
                    'holding_days': holding_days
                }
            }

        except Exception as e:
            logger.error(f"Error al obtener rendimiento de inversión {investment_id}: {e}")
            raise

    def close(self):
        """Cerrar sesión de base de datos."""
        if self._db_session:
            self._db_session.close()
