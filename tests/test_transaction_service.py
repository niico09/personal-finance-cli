"""Tests para el servicio de transacciones."""

from __future__ import annotations

import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, patch

from src.services.transaction_service import TransactionService
from src.database.models import Transaction, Category, Account, TransactionType


class TestTransactionService:
    """Tests para TransactionService."""

    @pytest.fixture
    def mock_session(self):
        """Mock de sesión de base de datos."""
        return Mock()

    @pytest.fixture
    def service(self, mock_session):
        """Instancia del servicio con mock de sesión."""
        return TransactionService(db_session=mock_session)

    def test_create_transaction_success(self, service, mock_session):
        """Test crear transacción exitosamente."""
        # Arrange
        mock_category = Mock()
        mock_category.id = "cat-123"
        mock_account = Mock()
        mock_account.id = "acc-456"

        service._get_or_create_category = Mock(return_value=mock_category)
        service._get_or_create_account = Mock(return_value=mock_account)

        # Act
        result = service.create_transaction(
            amount=Decimal("100.50"),
            description="Test transaction",
            transaction_type=TransactionType.EXPENSE,
            category_name="food",
            account_name="default"
        )

        # Assert
        assert isinstance(result, Transaction)
        assert result.amount == Decimal("100.50")
        assert result.description == "Test transaction"
        assert result.transaction_type == TransactionType.EXPENSE
        assert result.category_id == "cat-123"
        assert result.account_id == "acc-456"

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_create_transaction_with_tags(self, service, mock_session):
        """Test crear transacción con tags."""
        # Arrange
        mock_category = Mock()
        mock_category.id = "cat-123"
        mock_account = Mock()
        mock_account.id = "acc-456"

        service._get_or_create_category = Mock(return_value=mock_category)
        service._get_or_create_account = Mock(return_value=mock_account)

        # Act
        result = service.create_transaction(
            amount=Decimal("50.00"),
            description="Lunch",
            transaction_type=TransactionType.EXPENSE,
            tags=["restaurant", "lunch"]
        )

        # Assert
        assert result.tags == '["restaurant", "lunch"]'

    def test_create_transaction_database_error(self, service, mock_session):
        """Test error en base de datos al crear transacción."""
        # Arrange
        mock_session.commit.side_effect = Exception("Database error")
        service._get_or_create_category = Mock(return_value=Mock(id="cat-123"))
        service._get_or_create_account = Mock(return_value=Mock(id="acc-456"))

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            service.create_transaction(
                amount=Decimal("100.00"),
                description="Test",
                transaction_type=TransactionType.EXPENSE
            )

        mock_session.rollback.assert_called_once()

    def test_get_transactions_default_params(self, service, mock_session):
        """Test obtener transacciones con parámetros por defecto."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        result = service.get_transactions()

        # Assert
        assert result == []
        mock_session.query.assert_called_once_with(Transaction)

    def test_get_or_create_category_existing(self, service, mock_session):
        """Test obtener categoría existente."""
        # Arrange
        mock_category = Mock()
        mock_category.name = "food"
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_category

        # Act
        result = service._get_or_create_category("food")

        # Assert
        assert result == mock_category
        mock_session.add.assert_not_called()

    def test_get_or_create_category_new(self, service, mock_session):
        """Test crear nueva categoría."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = service._get_or_create_category("new_category")

        # Assert
        assert isinstance(result, Category)
        assert result.name == "new_category"
        assert result.description == "Categoría new_category"
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    def test_get_or_create_account_new(self, service, mock_session):
        """Test crear nueva cuenta."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = service._get_or_create_account("new_account")

        # Assert
        assert isinstance(result, Account)
        assert result.name == "new_account"
        assert result.account_type == "general"
        assert result.balance == Decimal('0')
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
