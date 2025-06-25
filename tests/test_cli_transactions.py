"""Tests para los comandos CLI de transacciones."""

from __future__ import annotations

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch
from typer.testing import CliRunner

from src.cli.commands.transactions import transactions_app
from src.database.models import Transaction, TransactionType


class TestTransactionsCLI:
    """Tests para comandos CLI de transacciones."""

    @pytest.fixture
    def runner(self):
        """Runner para testing de CLI."""
        return CliRunner()

    @patch('src.cli.commands.transactions.TransactionService')
    def test_add_transaction_success(self, mock_service_class, runner):
        """Test agregar transacción exitosamente."""
        # Arrange
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        mock_transaction = Mock()
        mock_transaction.id = "trans-123"
        mock_transaction.amount = Decimal("25.50")
        mock_transaction.description = "Test transaction"
        mock_transaction.transaction_type = TransactionType.EXPENSE
        mock_transaction.payment_method = "cash"
        mock_transaction.transaction_date.strftime.return_value = "2025-06-23 12:00"
        mock_transaction.category.name = "food"
        mock_transaction.parsed_tags = ["restaurant", "lunch"]
        mock_transaction.notes = None

        mock_service.create_transaction.return_value = mock_transaction

        # Act
        result = runner.invoke(transactions_app, [
            "add", "25.50", "Test transaction",
            "--category", "food",
            "--type", "expense",
            "--tags", "restaurant,lunch"
        ])

        # Assert
        assert result.exit_code == 0
        assert "✅ Transacción agregada exitosamente" in result.stdout
        assert "25.50" in result.stdout
        assert "Test transaction" in result.stdout
        assert "food" in result.stdout

        mock_service.create_transaction.assert_called_once()
        mock_service.close.assert_called_once()

    @patch('src.cli.commands.transactions.TransactionService')
    def test_add_transaction_invalid_type(self, mock_service_class, runner):
        """Test agregar transacción con tipo inválido."""
        # Act
        result = runner.invoke(transactions_app, [
            "add", "100.00", "Test",
            "--type", "invalid_type"
        ])

        # Assert
        assert result.exit_code == 1
        assert "❌ Tipo de transacción debe ser 'income' o 'expense'" in result.stdout

    @patch('src.cli.commands.transactions.TransactionService')
    def test_add_transaction_service_error(self, mock_service_class, runner):
        """Test error del servicio al agregar transacción."""
        # Arrange
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.create_transaction.side_effect = Exception("Service error")

        # Act
        result = runner.invoke(transactions_app, [
            "add", "100.00", "Test transaction"
        ])

        # Assert
        assert result.exit_code == 1
        assert "❌ Error al agregar transacción" in result.stdout

    @patch('src.cli.commands.transactions.TransactionService')
    def test_list_transactions_success(self, mock_service_class, runner):
        """Test listar transacciones exitosamente."""
        # Arrange
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        mock_transaction = Mock()
        mock_transaction.id = "trans-123"
        mock_transaction.transaction_date.strftime.return_value = "2025-06-23"
        mock_transaction.description = "Test transaction"
        mock_transaction.category.name = "food"
        mock_transaction.transaction_type = TransactionType.EXPENSE
        mock_transaction.amount = Decimal("25.50")

        mock_service.get_transactions.return_value = [mock_transaction]
        mock_service.get_total_income.return_value = Decimal("0.00")
        mock_service.get_total_expenses.return_value = Decimal("25.50")

        # Act
        result = runner.invoke(transactions_app, ["list"])

        # Assert
        assert result.exit_code == 0
        assert "Test transaction" in result.stdout
        assert "25.50" in result.stdout
        assert "📋 Últimas" in result.stdout

        mock_service.get_transactions.assert_called_once()
        mock_service.close.assert_called_once()

    @patch('src.cli.commands.transactions.TransactionService')
    def test_list_transactions_with_filters(self, mock_service_class, runner):
        """Test listar transacciones con filtros."""
        # Arrange
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_transactions.return_value = []
        mock_service.get_total_income.return_value = Decimal("0.00")
        mock_service.get_total_expenses.return_value = Decimal("0.00")

        # Act
        result = runner.invoke(transactions_app, [
            "list",
            "--limit", "10",
            "--type", "expense",
            "--category", "food"
        ])

        # Assert
        assert result.exit_code == 0
        mock_service.get_transactions.assert_called_once_with(
            limit=10,
            transaction_type=TransactionType.EXPENSE,
            category_name="food"
        )

    @patch('src.cli.commands.transactions.TransactionService')
    def test_summary_transactions(self, mock_service_class, runner):
        """Test resumen de transacciones."""
        # Arrange
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_total_income.return_value = Decimal("1000.00")
        mock_service.get_total_expenses.return_value = Decimal("750.00")
        mock_service.get_transaction_count.return_value = 15

        # Act
        result = runner.invoke(transactions_app, ["summary"])

        # Assert
        assert result.exit_code == 0
        assert "💰 Total Ingresos" in result.stdout
        assert "1000.00" in result.stdout
        assert "750.00" in result.stdout
        assert "250.00" in result.stdout  # Balance
        assert "15" in result.stdout

    def test_add_transaction_invalid_amount(self, runner):
        """Test agregar transacción con monto inválido."""
        # Act
        result = runner.invoke(transactions_app, [
            "add", "invalid_amount", "Test transaction"
        ])

        # Assert
        assert result.exit_code != 0
