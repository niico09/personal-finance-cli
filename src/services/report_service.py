"""Servicio de generación de reportes."""

from __future__ import annotations

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any, Tuple
from calendar import monthrange

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, extract, desc

from src.database.connection import create_db_session
from src.database.models import Transaction, Investment, Budget, Category, Account, TransactionType
from src.utils.logging import get_logger

logger = get_logger(__name__)


class ReportService:
    """Servicio para generación de reportes."""

    def __init__(self, db_session: Optional[Session] = None):
        """Inicializar servicio de reportes."""
        self._db_session = db_session
    @property
    def db_session(self) -> Session:
        """Obtener sesión de base de datos."""
        if self._db_session is None:
            self._db_session = create_db_session()
        return self._db_session

    def generate_monthly_report(self, year: int, month: int) -> Dict[str, Any]:
        """Generar reporte mensual completo."""
        try:
            # Calcular fechas del mes
            start_date = date(year, month, 1)
            _, last_day = monthrange(year, month)
            end_date = date(year, month, last_day)

            # Obtener datos de transacciones
            transactions_data = self._get_transactions_summary(start_date, end_date)

            # Obtener datos de presupuesto si existe
            budget_data = self._get_budget_analysis(year, month)

            # Obtener datos de inversiones
            investments_data = self._get_investments_summary()

            # Generar análisis de tendencias
            trends_data = self._get_monthly_trends(year, month)

            return {
                'period': {
                    'year': year,
                    'month': month,
                    'start_date': start_date,
                    'end_date': end_date,
                    'month_name': start_date.strftime('%B %Y')
                },
                'transactions': transactions_data,
                'budget': budget_data,
                'investments': investments_data,
                'trends': trends_data,
                'generated_at': datetime.now()
            }

        except Exception as e:
            logger.error(f"Error al generar reporte mensual {year}-{month}: {e}")
            raise

    def generate_yearly_report(self, year: int) -> Dict[str, Any]:
        """Generar reporte anual completo."""
        try:
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)

            # Datos de transacciones anuales
            transactions_data = self._get_transactions_summary(start_date, end_date)

            # Análisis mensual del año
            monthly_analysis = []
            for month in range(1, 13):
                month_start = date(year, month, 1)
                _, last_day = monthrange(year, month)
                month_end = date(year, month, last_day)

                month_data = self._get_transactions_summary(month_start, month_end)
                monthly_analysis.append({
                    'month': month,
                    'month_name': month_start.strftime('%B'),
                    **month_data
                })

            # Datos de inversiones
            investments_data = self._get_investments_summary()

            # Análisis de crecimiento anual
            growth_analysis = self._get_yearly_growth_analysis(year)

            return {
                'period': {
                    'year': year,
                    'start_date': start_date,
                    'end_date': end_date
                },
                'annual_summary': transactions_data,
                'monthly_breakdown': monthly_analysis,
                'investments': investments_data,
                'growth_analysis': growth_analysis,
                'generated_at': datetime.now()
            }

        except Exception as e:
            logger.error(f"Error al generar reporte anual {year}: {e}")
            raise

    def generate_category_report(
        self,
        start_date: date,
        end_date: date,
        category_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generar reporte por categorías."""
        try:
            query = self.db_session.query(Transaction).filter(
                and_(
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date
                )
            )

            if category_name:
                query = query.join(Category).filter(Category.name == category_name)

            # Análisis por categoría
            category_analysis = (
                query.join(Category)
                .with_entities(
                    Category.name,
                    Transaction.transaction_type,
                    func.sum(Transaction.amount).label('total'),
                    func.count(Transaction.id).label('count'),
                    func.avg(Transaction.amount).label('average')
                )
                .group_by(Category.name, Transaction.transaction_type)
                .order_by(desc('total'))
                .all()
            )

            # Organizar datos por categoría
            categories = {}
            for cat_name, trans_type, total, count, average in category_analysis:
                if cat_name not in categories:
                    categories[cat_name] = {
                        'name': cat_name,
                        'income': Decimal('0'),
                        'expense': Decimal('0'),
                        'transactions_count': 0,
                        'average_transaction': Decimal('0')
                    }

                if trans_type == TransactionType.INCOME:
                    categories[cat_name]['income'] = total
                elif trans_type == TransactionType.EXPENSE:
                    categories[cat_name]['expense'] = total

                categories[cat_name]['transactions_count'] += count

            # Calcular promedios y balances
            for cat_data in categories.values():
                cat_data['net_amount'] = cat_data['income'] - cat_data['expense']
                if cat_data['transactions_count'] > 0:
                    total_amount = cat_data['income'] + cat_data['expense']
                    cat_data['average_transaction'] = total_amount / cat_data['transactions_count']

            # Ordenar por gasto total
            categories_list = sorted(
                categories.values(),
                key=lambda x: x['expense'],
                reverse=True
            )

            return {
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                },
                'category_filter': category_name,
                'categories': categories_list,
                'summary': {
                    'total_categories': len(categories),
                    'total_income': sum(cat['income'] for cat in categories.values()),
                    'total_expense': sum(cat['expense'] for cat in categories.values()),
                    'total_transactions': sum(cat['transactions_count'] for cat in categories.values())
                },
                'generated_at': datetime.now()
            }

        except Exception as e:
            logger.error(f"Error al generar reporte de categorías: {e}")
            raise

    def generate_cash_flow_report(
        self,
        start_date: date,
        end_date: date,
        granularity: str = "daily"
    ) -> Dict[str, Any]:
        """Generar reporte de flujo de efectivo."""
        try:
            # Validar granularidad
            if granularity not in ["daily", "weekly", "monthly"]:
                raise ValueError("Granularidad debe ser: daily, weekly, monthly")

            # Obtener transacciones del período
            transactions = (
                self.db_session.query(Transaction)
                .filter(
                    and_(
                        Transaction.transaction_date >= start_date,
                        Transaction.transaction_date <= end_date
                    )
                )
                .order_by(Transaction.transaction_date)
                .all()
            )

            # Generar datos de flujo de efectivo
            cash_flow_data = []
            current_date = start_date
            running_balance = Decimal('0')

            while current_date <= end_date:
                # Determinar período actual
                if granularity == "daily":
                    period_end = current_date
                    next_date = current_date + timedelta(days=1)
                elif granularity == "weekly":
                    period_end = current_date + timedelta(days=6)
                    next_date = current_date + timedelta(days=7)
                else:  # monthly
                    if current_date.month == 12:
                        period_end = date(current_date.year + 1, 1, 1) - timedelta(days=1)
                        next_date = date(current_date.year + 1, 1, 1)
                    else:
                        period_end = date(current_date.year, current_date.month + 1, 1) - timedelta(days=1)
                        next_date = date(current_date.year, current_date.month + 1, 1)

                # Filtrar transacciones del período
                period_transactions = [
                    t for t in transactions
                    if current_date <= t.transaction_date.date() <= period_end
                ]

                # Calcular totales del período
                period_income = sum(
                    t.amount for t in period_transactions
                    if t.transaction_type == TransactionType.INCOME
                )
                period_expense = sum(
                    t.amount for t in period_transactions
                    if t.transaction_type == TransactionType.EXPENSE
                )

                period_net = period_income - period_expense
                running_balance += period_net

                cash_flow_data.append({
                    'period_start': current_date,
                    'period_end': period_end,
                    'income': period_income,
                    'expense': period_expense,
                    'net_flow': period_net,
                    'running_balance': running_balance,
                    'transactions_count': len(period_transactions)
                })

                current_date = next_date

            return {
                'period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'granularity': granularity
                },
                'cash_flow': cash_flow_data,
                'summary': {
                    'total_income': sum(cf['income'] for cf in cash_flow_data),
                    'total_expense': sum(cf['expense'] for cf in cash_flow_data),
                    'net_flow': sum(cf['net_flow'] for cf in cash_flow_data),
                    'final_balance': cash_flow_data[-1]['running_balance'] if cash_flow_data else Decimal('0'),
                    'periods_count': len(cash_flow_data)
                },
                'generated_at': datetime.now()
            }

        except Exception as e:
            logger.error(f"Error al generar reporte de flujo de efectivo: {e}")
            raise

    def _get_transactions_summary(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Obtener resumen de transacciones para un período."""
        transactions = (
            self.db_session.query(Transaction)
            .filter(
                and_(
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date
                )
            )
            .all()
        )

        income_total = sum(
            t.amount for t in transactions
            if t.transaction_type == TransactionType.INCOME
        )
        expense_total = sum(
            t.amount for t in transactions
            if t.transaction_type == TransactionType.EXPENSE
        )

        # Top categorías de gastos
        expense_by_category = {}
        for t in transactions:
            if t.transaction_type == TransactionType.EXPENSE:
                cat_name = t.category.name if t.category else "Sin categoría"
                expense_by_category[cat_name] = expense_by_category.get(cat_name, Decimal('0')) + t.amount

        top_categories = sorted(
            expense_by_category.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return {
            'income_total': income_total,
            'expense_total': expense_total,
            'net_amount': income_total - expense_total,
            'transactions_count': len(transactions),
            'average_transaction': sum(t.amount for t in transactions) / len(transactions) if transactions else Decimal('0'),
            'top_expense_categories': [
                {'name': cat, 'amount': amount}
                for cat, amount in top_categories
            ]
        }

    def _get_budget_analysis(self, year: int, month: int) -> Optional[Dict[str, Any]]:
        """Obtener análisis de presupuesto para un mes específico."""
        try:
            from src.services.budget_service import BudgetService

            budget_service = BudgetService(self.db_session)
            budget = budget_service.get_current_budget(year, month)

            if budget:
                return budget_service.get_budget_analysis(budget.id)

            return None

        except Exception as e:
            logger.error(f"Error al obtener análisis de presupuesto: {e}")
            return None

    def _get_investments_summary(self) -> Dict[str, Any]:
        """Obtener resumen de inversiones."""
        try:
            from src.services.investment_service import InvestmentService

            investment_service = InvestmentService(self.db_session)
            return investment_service.get_portfolio_summary()

        except Exception as e:
            logger.error(f"Error al obtener resumen de inversiones: {e}")
            return {}

    def _get_monthly_trends(self, year: int, month: int) -> Dict[str, Any]:
        """Obtener tendencias mensuales."""
        # Comparar con mes anterior
        if month == 1:
            prev_year, prev_month = year - 1, 12
        else:
            prev_year, prev_month = year, month - 1

        current_start = date(year, month, 1)
        _, current_last_day = monthrange(year, month)
        current_end = date(year, month, current_last_day)

        prev_start = date(prev_year, prev_month, 1)
        _, prev_last_day = monthrange(prev_year, prev_month)
        prev_end = date(prev_year, prev_month, prev_last_day)

        current_data = self._get_transactions_summary(current_start, current_end)
        prev_data = self._get_transactions_summary(prev_start, prev_end)

        # Calcular cambios porcentuales
        income_change = self._calculate_percentage_change(
            prev_data['income_total'], current_data['income_total']
        )
        expense_change = self._calculate_percentage_change(
            prev_data['expense_total'], current_data['expense_total']
        )

        return {
            'previous_month': {
                'year': prev_year,
                'month': prev_month,
                'data': prev_data
            },
            'current_month': {
                'year': year,
                'month': month,
                'data': current_data
            },
            'changes': {
                'income_change_percentage': income_change,
                'expense_change_percentage': expense_change,
                'income_trend': 'up' if income_change > 0 else 'down' if income_change < 0 else 'stable',
                'expense_trend': 'up' if expense_change > 0 else 'down' if expense_change < 0 else 'stable'
            }
        }

    def _get_yearly_growth_analysis(self, year: int) -> Dict[str, Any]:
        """Obtener análisis de crecimiento anual."""
        try:
            # Comparar con año anterior
            current_start = date(year, 1, 1)
            current_end = date(year, 12, 31)

            prev_start = date(year - 1, 1, 1)
            prev_end = date(year - 1, 12, 31)

            current_data = self._get_transactions_summary(current_start, current_end)
            prev_data = self._get_transactions_summary(prev_start, prev_end)

            # Calcular tasas de crecimiento
            income_growth = self._calculate_percentage_change(
                prev_data['income_total'], current_data['income_total']
            )
            expense_growth = self._calculate_percentage_change(
                prev_data['expense_total'], current_data['expense_total']
            )

            return {
                'previous_year': prev_data,
                'current_year': current_data,
                'growth_rates': {
                    'income_growth': income_growth,
                    'expense_growth': expense_growth,
                    'net_growth': self._calculate_percentage_change(
                        prev_data['net_amount'], current_data['net_amount']
                    )
                }
            }

        except Exception as e:
            logger.error(f"Error al obtener análisis de crecimiento: {e}")
            return {}

    def _calculate_percentage_change(self, old_value: Decimal, new_value: Decimal) -> float:
        """Calcular cambio porcentual."""
        if old_value == 0:
            return 100.0 if new_value > 0 else 0.0

        return float((new_value - old_value) / old_value * 100)

    def close(self):
        """Cerrar sesión de base de datos."""
        if self._db_session:
            self._db_session.close()
