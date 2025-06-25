"""
Sales Command - Sistema de gestión financiera personal.

Un sistema completo de línea de comandos para gestión financiera personal
que incluye seguimiento de gastos, presupuestos, inversiones y reportes.
"""

__version__ = "1.0.0"
__author__ = "Sales Command Team"
__email__ = "dev@salescommand.com"

from src.config.settings import Settings, get_settings
from src.database.models import Transaction, Budget, Investment

__all__ = [
    "Settings",
    "get_settings",
    "Transaction",
    "Budget",
    "Investment",
]
