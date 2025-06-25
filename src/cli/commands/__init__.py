"""Comandos CLI de Sales Command."""

from .transactions import transactions_app
from .budgets import budgets_app
from .investments import investments_app
from .reports import reports_app

__all__ = [
    "transactions_app",
    "budgets_app",
    "investments_app",
    "reports_app"
]
